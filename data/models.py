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
    d_o = fields.FloatField(description="外径 (m)")  # 换热管外径
    lambda_t = fields.FloatField(description="管壁导热系数 (W/(m·K))")
    heat_exchange_area = fields.FloatField(null=True, description="换热面积 (m²)")
    tube_passes = fields.IntField(null=True, description="管程数")
    shell_passes = fields.IntField(null=True, description="壳程数")
    tube_wall_thickness = fields.FloatField(null=True, description="换热管壁厚 (m)")
    tube_length = fields.FloatField(null=True, description="换热管长度 (m)")
    tube_count = fields.IntField(null=True, description="换热管数")
    tube_arrangement = fields.CharField(max_length=50, null=True, description="换热管布置形式")
    tube_pitch = fields.FloatField(null=True, description="换热管间距 (m)")
    shell_inner_diameter = fields.FloatField(null=True, description="壳体内径 (m)")
    baffle_type = fields.CharField(max_length=50, null=True, description="折流板类型")
    baffle_cut_ratio = fields.FloatField(null=True, description="折流板切口率")
    baffle_spacing = fields.FloatField(null=True, description="折流板间距 (m)")

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
    """模型参数表，保存a、p和b三个参数的实时值，按points分别训练"""
    id = fields.IntField(pk=True, description="主键")
    heat_exchanger = fields.ForeignKeyField("models.HeatExchanger", related_name="model_parameters", description="外键，连接换热器表")
    timestamp = fields.DatetimeField(description="时间戳，每天三点更新一次")
    points = fields.IntField(description="测量点（整型），对应壳侧分段")
    side = fields.CharEnumField(SideEnum, description="侧标识，固定为tube")
    a = fields.FloatField(description="模型参数a")
    p = fields.FloatField(description="模型参数p")
    b = fields.FloatField(description="模型参数b")

    class Meta:
        table = "model_parameters"
        unique_together = ("heat_exchanger", "timestamp", "points", "side")


# 新增：总传热系数管理表
class KManagement(Model):
    """总传热系数管理表，包含LMTD法计算的K、K预测值、K实际值"""
    id = fields.IntField(pk=True, description="主键")
    heat_exchanger = fields.ForeignKeyField("models.HeatExchanger", related_name="k_management", description="外键，连接换热器表")
    timestamp = fields.DatetimeField(description="时间戳")
    points = fields.IntField(description="测量点（整型）")
    side = fields.CharEnumField(SideEnum, description="侧标识")
    K_LMTD = fields.FloatField(description="LMTD法计算的总传热系数 (W/(m²·K))")
    K_predicted = fields.FloatField(description="预测总传热系数 (W/(m²·K))")
    K_actual = fields.FloatField(description="实际总传热系数 (W/(m²·K))")

    class Meta:
        table = "k_management"
        unique_together = ("heat_exchanger", "timestamp", "points", "side")

