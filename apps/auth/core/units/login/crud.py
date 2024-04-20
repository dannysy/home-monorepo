from datetime import datetime
from sqlalchemy import select

from house.basic.utils import get_hash
from house.basic.crud import CRUD
from house.units.app_user.crud import CRUDapp_user
from house.basic.enum_const import Receiver
from house.units.login.const import MAX_1H_SMS, MAX_1H_PASSWORD, MAX_TRIES_SMS, OUT_OF_TRIES_SMS, \
    OUT_OF_TRIES_PASSWORD, WAIT_TIME_FAIL_PASSWORD, OUT_OF_LIMIT_SMS
from house.units.login.model import LoginModel
from house.units.login.schema import LoginSendRowSchema, CreateLoginSchema, LoginSMSSchema, LoginPswrdSchema
from house.units.user.crud import CRUDuser
from house.units.user.model import UserModel


async def send_sms(app_id: int, country_code: int, phone_number: int, code: int):
    pass


class CRUDlogin(CRUD):
    # TODO: во все методы можно добавить логику добавления id в спамерские временные списки

    send_schema = LoginSendRowSchema

    async def create(self, msg: CreateLoginSchema):
        # Закрываем все предыдущие незавершенные логины с данного устройства
        logined = (await self.session.execute(
            select(LoginModel).
            where(LoginModel.sender_app_id == msg.sender_app_id).
            where(LoginModel.success == None)
        )).scalars().all()

        _now = datetime.utcnow()
        if len(logined) > 0:
            for obj in logined:
                obj.success = False
                obj.finish_datetime = _now
                self.session.add(obj)

            await self.session.commit()

        # Подтягиваем статистики и статус возможности создания объекта логина
        available, wait_minutes, reason, avlbl_pswrd_tries = await self.check_availability(
            app_id=msg.sender_app_id,
            country_code=msg.country_code,
            phone_number=msg.phone_number,
            sms=True,
            password=True
        )
        if available:  # Логин возможен
            obj = LoginModel(
                created_date=datetime.utcnow(),
                local_id=msg.local_id,
                app_id=msg.sender_app_id,
                app_type=msg.sender_app_type,
                country_code=msg.country_code,
                phone_number=msg.phone_number,
                sms_code=11111,  # random.randint(1, 99999),
                cnt_sms_tries=0
            )
            self.session.add(obj)
            await self.session.commit()
            self._send_normal_row(obj, [Receiver(app_id=msg.sender_app_id), ])
            await send_sms(obj.sender_app_id, obj.country_code, obj.phone_number, obj.sms_code)
        else:  # Логин невозможен
            # TODO: Необходимо протестировать эту ветку логики
            send_msg = LoginSendRowSchema(
                server_time=_now,
                receiver_last_connected=_now,
                receiver_app_id=msg.sender_app_id,
                local_id=msg.local_login_id,
                app_id=msg.sender_app_id,
                cnt_sms_tries=0,
                success=False,
                reason=reason,
                wait_minutes=wait_minutes
            )
            self._send_normal_row(send_msg, [Receiver(app_id=msg.sender_app_id), ])

    async def verify_sms_code(self, login_obj: LoginModel, msg: LoginSMSSchema):
        if login_obj.cnt_sms_tries >= MAX_TRIES_SMS:
            login_obj.success = False
            login_obj.finish_datetime = datetime.utcnow()
            login_obj.reason = OUT_OF_TRIES_SMS
        elif login_obj.sms_code != msg.sms_code:
            login_obj.passed_sms = False
            login_obj.cnt_sms_tries += 1

            if login_obj.cnt_sms_tries >= MAX_TRIES_SMS:
                available, cnt_minutes, reason, _ = await self.check_availability(
                    app_id=msg.sender_app_id,
                    country_code=msg.сountry_code,
                    phone_number=msg.phone_number,
                    sms=True,
                    password=False
                )
                if not available:
                    login_obj.success = False
                    login_obj.finish_datetime = datetime.utcnow()
                    login_obj.reason = reason
                    login_obj.wait_minutes = cnt_minutes
        elif login_obj.sms_code == msg.sms_code:
            login_obj.cnt_sms_tries += 1
            login_obj.passed_sms = True
            existed_user = (await self.session.execute(
                select(UserModel).
                where(UserModel.phone_number == login_obj.phone_number).
                where(UserModel.country_code == login_obj.country_code).
                where(UserModel.app_type == login_obj.app_type).
                where(UserModel.deactivated == False)
            )).scalar()

            if existed_user is None:
                login_obj.success = True
                login_obj.finish_datetime = datetime.utcnow()
                login_obj.new_user = True
            else:
                login_obj.new_user = False
                login_obj.user_id = existed_user.id

                available, cnt_minutes, reason, avlbl_pswrd_tries = await self.check_availability(
                        app_id=msg.sender_app_id,
                        country_code=login_obj.country_code,
                        phone_number=login_obj.phone_number,
                        sms=False,
                        password=True
                    )
                if not available:
                    login_obj.success = False
                    login_obj.finish_datetime = datetime.utcnow()
                    login_obj.reason = reason
                    login_obj.wait_minutes = cnt_minutes
                else:
                    if existed_user.hashed_password is None:
                        login_obj.success = True
                        login_obj.finish_datetime = datetime.utcnow()
                    else:
                        login_obj.hashed_password = existed_user.hashed_password
                        login_obj.salt = existed_user.salt

        await self.after_update(login_obj)

    async def verify_pswrd(self, login_obj: LoginModel, msg: LoginPswrdSchema):
        available, cnt_minutes, reason, avlbl_pswrd_tries = await self.check_availability(
            app_id=msg.sender_app_id,
            country_code=login_obj.country_code,
            phone_number=login_obj.phone_number,
            sms=False,
            password=True
        )
        if not available:
            login_obj.success = False
            login_obj.finish_datetime = datetime.utcnow()
            login_obj.reason = reason
            login_obj.wait_minutes = cnt_minutes
        elif get_hash(str(msg.password), login_obj.salt) == login_obj.hashed_password:
            login_obj.success = True
            login_obj.finish_datetime = datetime.utcnow()
        else:  # Ввел неверный пароль
            # TODO: Необходимо вносить данные по неудачным попыткам в таблицу статистики
            if avlbl_pswrd_tries == 1:
                login_obj.success = False
                login_obj.finish_datetime = datetime.utcnow()
                login_obj.reason = OUT_OF_TRIES_PASSWORD
                login_obj.wait_minutes = WAIT_TIME_FAIL_PASSWORD
            else:
                login_obj.passed_password = False
        await self.after_update(login_obj)

    async def after_update(self, login_obj: LoginModel):
        if login_obj.new_user and login_obj.success:
            user = await CRUDuser(self.session).create(login_obj)
            login_obj.user_id = user.id

        self.session.add(login_obj)
        await self.session.commit()

        self._send_normal_row(login_obj, [Receiver(app_id=login_obj.sender_app_id), ])
        if login_obj.success:
            await CRUDapp_user(self.session).login(login_obj)

    async def check_availability(self, app_id: int, country_code: int, phone_number: int,
                                 sms: bool = True, password: bool = True) -> (bool, int, str, int):
        # TODO: Описать логику действий при проверке возможности логина, определить входные параметры
        if sms:
            # TODO: Необходимо прописать логику сбора статистки по смс
            #  для данного устройства и номера телефона
            cnt_sms = 1
            last_sms = datetime.utcnow()
        else:
            cnt_sms = 0

        if password:
            # TODO: Необходимо прописать логику сбора статистки по паролям
            #  для данного устройства и номера телефона
            cnt_pswrd = 1
            last_password = datetime.utcnow()
        else:
            cnt_pswrd = 0

        cnt_minutes = 0
        if cnt_sms < MAX_1H_SMS and cnt_pswrd <= MAX_1H_PASSWORD:
            status = True
            reason = ''
            avlbl_pswrd_tries = MAX_1H_PASSWORD - cnt_pswrd
        else:
            status = False
            avlbl_pswrd_tries = 0
            if cnt_sms >= MAX_1H_SMS:
                cnt_minutes = min((datetime.utcnow() - last_sms).seconds, 60)
                reason = OUT_OF_LIMIT_SMS

            if cnt_pswrd > MAX_1H_PASSWORD:
                reason = OUT_OF_TRIES_PASSWORD
                cnt_minutes = max(
                    min((datetime.utcnow() - last_password).seconds, 60),
                    cnt_minutes
                )
        return status, cnt_minutes, reason, avlbl_pswrd_tries