from marshmallow import Schema, fields

class InternalHistorySchema(Schema):
    alertDate = fields.DateTime()
    title = fields.Str()
    data = fields.Str()

class PublicHistorySchema(Schema):
    data = fields.Str()
    date = fields.Str()
    time = fields.Str()
    datetime = fields.DateTime()

class PublicUpdatesSchema(Schema):
    data = fields.List(fields.Str())
    id = fields.Int()
    title = fields.Str()

class ApiAlarmSchema(Schema):
    location = fields.Str()
    timestamp = fields.DateTime()