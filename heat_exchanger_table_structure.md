# heat_exchanger 表结构

## 字段信息

| 字段名 | 类型 | 允许为空 | 主键 | 默认值 | 额外信息 |
|-------|------|---------|------|--------|---------|
| id | int | NO | PRI | None | auto_increment |
| type | varchar(50) | NO | | None | |
| tube_side_fluid | varchar(50) | NO | | None | |
| shell_side_fluid | varchar(50) | NO | | None | |
| tube_section_count | int | NO | | None | |
| shell_section_count | int | NO | | None | |
| d_i_original | double | NO | | None | |
| d_o | double | NO | | None | |
| lambda_t | double | NO | | None | |
| heat_exchange_area | float | YES | | None | |
| tube_passes | int | YES | | None | |
| shell_passes | int | YES | | None | |
| tube_wall_thickness | float | YES | | None | |
| tube_length | float | YES | | None | |
| tube_count | int | YES | | None | |
| tube_arrangement | varchar(50) | YES | | None | |
| tube_pitch | float | YES | | None | |
| shell_inner_diameter | float | YES | | None | |
| baffle_type | varchar(50) | YES | | None | |
| baffle_cut_ratio | float | YES | | None | |
| baffle_spacing | float | YES | | None | |

## 字段说明

- **id**: 换热器ID，主键，自增
- **type**: 换热器类型
- **tube_side_fluid**: 管程流体
- **shell_side_fluid**: 壳程流体
- **tube_section_count**: 管段数量
- **shell_section_count**: 壳段数量
- **d_i_original**: 原始管内径
- **d_o**: 管外径
- **lambda_t**: 管材导热系数
- **heat_exchange_area**: 换热面积
- **tube_passes**: 管程数
- **shell_passes**: 壳程数
- **tube_wall_thickness**: 管壁厚度
- **tube_length**: 管长
- **tube_count**: 管数
- **tube_arrangement**: 管束排列方式
- **tube_pitch**: 管间距
- **shell_inner_diameter**: 壳体内径
- **baffle_type**: 折流板类型
- **baffle_cut_ratio**: 折流板切割率
- **baffle_spacing**: 折流板间距