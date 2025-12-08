from tortoise import Model, fields
from enum import Enum

# 侧标识枚举
class SideEnum(str, Enum):
    TUBE = "tube"  # 管侧
    SHELL = "shell"  # 壳侧

# 换热器表
class HeatExchanger(Model):
    """换热器信息表"""
    id = fields.IntField(pk=True, description="主键，换热器编号")
    type = fields.CharField(max_length=50, description="换热器种类")
    tube_side_fluid = fields.CharField(max_length=50, description="管侧工质")
    shell_side_fluid = fields.CharField(max_length=50, description="壳侧工质")
    tube_section_count = fields.IntField(description="管侧分段数")
    shell_section_count = fields.IntField(description="壳侧分段数")
    d_i_original = fields.FloatField(description="原始内径 (m)")
    d_o = fields.FloatField(description="外径 (m)")
    lambda_t = fields.FloatField(description="管壁导热系数 (W/(m·K))")

    class Meta:
        table = "heat_exchanger"

# 运行参数表
class OperationParameter(Model):
    """运行参数表"""
    id = fields.IntField(pk=True, description="主键")
    heat_exchanger = fields.ForeignKeyField("models.HeatExchanger", related_name="operation_parameters", description="外键，连接换热器表")
    timestamp = fields.DatetimeField(description="时间戳")
    points = fields.IntField(description="测量点（整型）")
    side = fields.CharEnumField(SideEnum, description="侧标识")
    temperature = fields.FloatField(description="温度 (°C)")
    pressure = fields.FloatField(description="压力 (Pa)")
    flow_rate = fields.FloatField(description="流量 (m³/s)")
    velocity = fields.FloatField(description="流速 (m/s)")

    class Meta:
        table = "operation_parameters"
        unique_together = ("heat_exchanger", "timestamp", "points", "side")

# 物性参数表
class PhysicalParameter(Model):
    """物性参数表"""
    id = fields.IntField(pk=True, description="主键")
    heat_exchanger = fields.ForeignKeyField("models.HeatExchanger", related_name="physical_parameters", description="外键，连接换热器表")
    timestamp = fields.DatetimeField(description="时间戳")
    points = fields.IntField(description="测量点（整型）")
    side = fields.CharEnumField(SideEnum, description="侧标识")
    density = fields.FloatField(description="密度 (kg/m³)")
    viscosity = fields.FloatField(description="动力粘度 (Pa·s)")
    thermal_conductivity = fields.FloatField(description="导热系数 (W/(m·K))")
    specific_heat = fields.FloatField(description="比热容 (J/(kg·K))")
    reynolds = fields.FloatField(description="雷诺数")
    prandtl = fields.FloatField(description="普朗特数")

    class Meta:
        table = "physical_parameters"
        unique_together = ("heat_exchanger", "timestamp", "points", "side")

# 性能参数表
class PerformanceParameter(Model):
    """性能参数表"""
    id = fields.IntField(pk=True, description="主键")
    heat_exchanger = fields.ForeignKeyField("models.HeatExchanger", related_name="performance_parameters", description="外键，连接换热器表")
    timestamp = fields.DatetimeField(description="时间戳")
    points = fields.IntField(description="测量点（整型）")
    side = fields.CharEnumField(SideEnum, description="侧标识")
    K = fields.FloatField(description="总传热系数 (W/(m²·K))")
    alpha_i = fields.FloatField(description="管侧传热系数 (W/(m²·K))")
    alpha_o = fields.FloatField(description="壳侧传热系数 (W/(m²·K))")
    heat_duty = fields.FloatField(description="热负荷 (W)")
    effectiveness = fields.FloatField(description="有效度")
    lmtd = fields.FloatField(description="对数平均温差 (°C)")

    class Meta:
        table = "performance_parameters"
        unique_together = ("heat_exchanger", "timestamp", "points", "side")

# 模型参数表
class ModelParameter(Model):
    """模型参数表，保存a、p和b三个参数的实时值"""
    id = fields.IntField(pk=True, description="主键")
    heat_exchanger = fields.ForeignKeyField("models.HeatExchanger", related_name="model_parameters", description="外键，连接换热器表")
    timestamp = fields.DatetimeField(description="时间戳，每天三点更新一次")
    a = fields.FloatField(description="模型参数a")
    p = fields.FloatField(description="模型