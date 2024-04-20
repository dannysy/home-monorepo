from apps.auth.core.schema import ReceivedBasic


class ReceivedCreateLogin(ReceivedBasic):
    country_code: int
    phone_number: int

#
# class LoginSMSSchema(InputMsgSchema):
#     id: int
#     sms_code: int
#
#
# class LoginPswrdSchema(InputMsgSchema):
#     id: int
#     password: int
#
#
# TABLE_ID = TableId.login
#
#
# class LoginSendRowSchema(SendRowSchema):
#     db_table_id: TableId = TABLE_ID
#
#     created_date: Optional[datetime] = None
#     id: Optional[int] = None
#     local_id: int
#     sender_app_id: int
#     user_id: Optional[int] = None
#     cnt_sms_tries: int
#     passed_sms: Optional[bool] = None
#     passed_password: Optional[bool] = None
#     success: Optional[bool] = None
#     reason: Optional[str] = None
#     wait_minutes: Optional[int] = None
#     finish_datetime: Optional[datetime] = None
#     new_user: Optional[bool] = None
#
#     model_config = ConfigDict(from_attributes=True)
#
#     @model_validator(mode='after')
#     def verify(self) -> 'LoginSendRowSchema':
#         if not self.success:
#             self.user_id = None
#         return self
#
#     @property
#     def row_updated_dtime(self) -> datetime:
#         return self.created_date
#
#
# add_schema_to_mapper(TABLE_ID, LoginSendRowSchema)
