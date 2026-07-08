from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.CharField(pk=True, max_length=36)
    email = fields.CharField(max_length=255, unique=True)
    role = fields.CharField(max_length=40, default="operator")
    created_at = fields.DatetimeField(auto_now_add=True)


class RefreshToken(Model):
    id = fields.CharField(pk=True, max_length=36)
    user = fields.ForeignKeyField("models.User", related_name="refresh_tokens")
    device_id = fields.CharField(max_length=255)
    token_hash = fields.TextField()
    expires_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        unique_together = (("user", "device_id"),)


class ProductionLine(Model):
    id = fields.CharField(pk=True, max_length=36)
    name = fields.CharField(max_length=120)
    plant = fields.CharField(max_length=120)
    status = fields.CharField(max_length=40)


class Machine(Model):
    id = fields.CharField(pk=True, max_length=36)
    line = fields.ForeignKeyField("models.ProductionLine", related_name="machines")
    name = fields.CharField(max_length=120)
    type = fields.CharField(max_length=60)
    threshold_profile = fields.JSONField(default=dict)


class SensorEvent(Model):
    id = fields.CharField(pk=True, max_length=36)
    machine = fields.ForeignKeyField("models.Machine", related_name="sensor_events")
    time = fields.DatetimeField()
    metric = fields.CharField(max_length=80)
    value = fields.FloatField()
    unit = fields.CharField(max_length=20)
    source = fields.CharField(max_length=80, default="mock")


class InspectionResult(Model):
    id = fields.CharField(pk=True, max_length=36)
    machine = fields.ForeignKeyField("models.Machine", related_name="inspection_results")
    captured_at = fields.DatetimeField()
    defect_score = fields.FloatField()
    label = fields.CharField(max_length=80)
    image_url = fields.CharField(max_length=500, null=True)


class QualityEvent(Model):
    id = fields.CharField(pk=True, max_length=36)
    line = fields.ForeignKeyField("models.ProductionLine", related_name="quality_events")
    machine = fields.ForeignKeyField("models.Machine", related_name="quality_events")
    severity = fields.CharField(max_length=40)
    status = fields.CharField(max_length=40, default="open")
    reason = fields.TextField()
    defect_score = fields.FloatField(default=0)
    opened_at = fields.DatetimeField()
    closed_at = fields.DatetimeField(null=True)


class ActionLog(Model):
    id = fields.CharField(pk=True, max_length=36)
    quality_event = fields.ForeignKeyField("models.QualityEvent", related_name="action_logs")
    actor = fields.ForeignKeyField("models.User", related_name="action_logs")
    action = fields.CharField(max_length=40)
    memo = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
