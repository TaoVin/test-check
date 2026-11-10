import sqlite3
import warnings

import pandas as pd

RAW_FIELD_CONFIG: dict[str, str] = {
    "*编码": "req_code",
    "*名称.简体中文": "req_name_zh",
    "名称.English": "name_en",
    "数据状态": "data_status",
    "创建人.工号": "creator_employee_no",
    "创建人.姓名": "creator_employee_name",
    "修改人.工号": "modifier_employee_no",
    "修改人.姓名": "modifier_employee_name",
    "使用状态": "usage_status",
    "创建时间": "created_at",
    "修改时间": "updated_at",
    "管理组织.编码": "management_org_code",
    "管理组织.名称": "management_org_name",
    "*创建组织.编码": "req_creation_org_code",
    "创建组织.名称": "creation_org_name",
    "*控制策略": "req_control_policy",
    "禁用人.工号": "disabler_employee_no",
    "禁用人.姓名": "disabler_employee_name",
    "禁用时间": "disabled_at",
    "*基本单位.编码": "req_base_unit_code",
    "基本单位.名称": "base_unit_name",
    "审核人.工号": "auditor_employee_no",
    "审核人.姓名": "auditor_employee_name",
    "审核日期": "audit_date",
    "描述.简体中文": "description_zh",
    "描述.English": "description_en",
    "旧物料编码": "old_material_code",
    "旧物料名称": "old_material_name",
    "规格型号.简体中文": "specification_zh",
    "规格型号.English": "specification_en",
    "物料分类.编码": "material_category_code",
    "物料分类.名称": "material_category_name",
    "物料形态(废弃)": "material_form_deprecated",
    "可受托(废弃)": "can_be_entrusted_deprecated",
    "启用辅助属性": "enable_aux_attribute",
    "图片": "image",
    "辅助单位.编码": "auxiliary_unit_code",
    "辅助单位.名称": "auxiliary_unit_name",
    "*换算方向": "req_conversion_direction",
    "农产品": "agricultural_product",
    "可抵扣率(%)": "deductible_rate_percent",
    "影响计划": "affect_planning",
    "启用版本管理": "enable_version_management",
    "影响库存": "affect_inventory",
    "版本编码规则.编码": "version_code_rule_code",
    "版本编码规则.名称": "version_code_rule_name",
    "辅助单位(2).编码": "auxiliary_unit_2_code",
    "辅助单位(2).名称": "auxiliary_unit_2_name",
    "套件": "kit",
    "重量单位.编码": "weight_unit_code",
    "重量单位.名称": "weight_unit_name",
    "毛重": "gross_weight",
    "净重": "net_weight",
    "尺寸单位.编码": "size_unit_code",
    "尺寸单位.名称": "size_unit_name",
    "长度": "length",
    "宽度": "width",
    "高度": "height",
    "容积单位.编码": "volume_unit_code",
    "容积单位.名称": "volume_unit_name",
    "容积": "volume",
    "启用人.工号": "enabler_employee_no",
    "启用人.姓名": "enabler_employee_name",
    "启用时间": "enabled_at",
    "面积单位.编码": "area_unit_code",
    "面积单位.名称": "area_unit_name",
    "面积": "area",
    "税收分类编码.编码": "tax_classification_code_code",
    "税收分类编码.名称": "tax_classification_code_name",
    "*税收优惠政策类型": "req_tax_preference_type",
    "享受税收优惠政策": "enjoy_tax_preference",
    "旧物料名称-废": "old_material_name_deprecated",
    "旧规格型号": "old_specification",
    "品牌": "brand",
    "软件介质": "software_medium",
    "设备类型": "device_type",
    "源单位.编码": "source_unit_code",
    "源单位.名称": "source_unit_name",
    "基本单位.编码": "base_unit_code",
    "*基本单位换算系数": "req_base_unit_conversion_factor",
    "*源单位换算系数": "req_source_unit_conversion_factor",
    "*换算类型": "req_conversion_type",
    "应用场景": "application_scenario",
    "单位转换实体id": "unit_conversion_entity_id",
    "源单位精度(废弃)": "source_unit_precision_deprecated",
    "*辅助属性.编码": "req_auxiliary_attribute_code",
    "辅助属性.名称": "auxiliary_attribute_name",
    "组合控制": "combination_control",
    "影响库存.1": "affect_inventory_2",  # 重复列，pandas 自动后缀 .1
    "影响成本": "affect_cost",
    "影响计划.1": "affect_planning_2",  # 重复列
    "已维护属性值": "maintained_attribute_value",
    "值范围控制": "value_range_control",
    "*分类标准编码.编码": "req_classification_standard_code",
    "分类标准编码.名称": "classification_standard_code_name",
    "物料分类编码.编码": "material_category_code_code",
    "物料分类编码.名称": "material_category_code_name",
    "默认分类标准": "default_classification_standard",
    "辅助属性值ID": "auxiliary_attribute_value_id",
    "辅助属性值编码": "auxiliary_attribute_value_code",
    "辅助属性值名称.简体中文": "auxiliary_attribute_value_name_zh",
    "辅助属性值名称.English": "auxiliary_attribute_value_name_en",
    "默认值": "default_value",
    "启用": "enabled",
    "辅助属性ID": "auxiliary_attribute_id",
    "名称": "check_name",
    "规格型号": "size",
    "单位": "unit",
    "type": "type",
    "原表序号": "_rowId"
}
EN_TO_ZH = {v: k for k, v in RAW_FIELD_CONFIG.items()}

import time

date = time.strftime("%Y%m%d%H%M%S", time.localtime())
DB = f"data.db"
BASE_TABLE = f"baseline"
CHECK_TABLE = f"check"

warnings.filterwarnings("ignore", category=UserWarning)


def init_material(path: str, db: str, table: str):
    df = pd.read_excel(path, engine="openpyxl")
    df = df.apply(lambda s: s.str.strip().fillna("") if s.dtype == object else s)
    str_cols = df.select_dtypes(include=["object", "string", "str"]).columns
    df[str_cols] = df[str_cols].apply(lambda s: s.str.strip().fillna(""))
    df.columns = [str(RAW_FIELD_CONFIG.get(c)).strip() for c in df.columns]
    df.insert(0, "_rowId", range(1, len(df) + 1))
    con = sqlite3.connect(db)
    df.to_sql(table, con, if_exists="replace", index=False)
    con.commit();
    con.close()
    print(f"已导入 {len(df)} 条到 {DB}/{table}")


duplicate_sql = """
                SELECT b.req_code, b.req_name_zh, b.specification_zh, b.brand, b.old_material_code, b.old_material_name
                FROM baseline b
                         INNER JOIN (SELECT req_name_zh,
                                            specification_zh,
                                            brand
                                     FROM baseline
                                     GROUP BY req_name_zh, specification_zh, brand
                                     HAVING COUNT(DISTINCT req_code) > 1) s ON b.req_name_zh = s.req_name_zh
                    AND (b.specification_zh = s.specification_zh)
                    AND (b.brand = s.brand)
                ORDER BY b.req_name_zh, b.specification_zh, b.brand \
                """


def analyse_duplicate(db: str, export_path: str | None = None):
    with sqlite3.connect(db) as con:
        duplicate_f = pd.read_sql_query(duplicate_sql, con=con)
        duplicate_f.columns = [EN_TO_ZH.get(c, c) for c in duplicate_f.columns]
        duplicate_f.to_excel(export_path or f"物料名称-规格型号-品牌一致，但有多个物料编号-{date}.xlsx", index=False)


check_sql = """
            SELECT c._rowId, c.check_name, c.size, c.brand, c.unit
            FROM "check" c
            WHERE EXISTS (SELECT 1 FROM `baseline` a WHERE c.check_name = a.req_name_zh AND c.size = a.specification_zh)
            """


def check_data(db: str, export_path: str | None = None):
    with sqlite3.connect(db) as con:
        duplicate_f = pd.read_sql_query(check_sql, con=con)
        duplicate_f.columns = [EN_TO_ZH.get(c, c) for c in duplicate_f.columns]
        duplicate_f.to_excel(export_path or f"物理名称+规格+品牌，物料主数据已存在的数据-{date}.xlsx", index=False)


CHECK_FIELD_CONFIG: dict[str, str] = {
    "名称": "check_name",
    "规格型号": "size",
    "品牌": "brand",
    "单位": "unit",
}


def init_check(path: str, db: str, table: str):
    df = pd.read_excel(path, engine="openpyxl")
    df = df.rename(columns=CHECK_FIELD_CONFIG)[list(CHECK_FIELD_CONFIG.values())]
    df = df.apply(lambda s: s.str.strip().fillna("") if s.dtype == object else s)
    df.insert(0, "_rowId", range(1, len(df) + 1))
    con = sqlite3.connect(db)
    df.to_sql(table, con, if_exists="replace", index=False)
    con.commit()
    con.close()


def do_init(file):
    init_material(file, DB, BASE_TABLE)


def do_analyse(file=None, out=None):
    if file:
        init_material(file, DB, BASE_TABLE)
    analyse_duplicate(DB, out)


def do_check(file, out=None):
    init_check(file, DB, CHECK_TABLE)
    check_data(DB, out)
#
# def build_parser():
#     p = argparse.ArgumentParser(
#         prog="main.py",
#         description="物料数据校验工具",
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         usage=(
#             "main.py -init -f FILE\n"
#             "       main.py -a [-f FILE] [-o FILE]\n"
#             "       main.py -c -f FILE [-o FILE]"
#         ),
#         epilog="""
# 示例:
#   python main.py -init -f "导出数据_物料_1109132856.xlsx"   初始化基础数据
#   python main.py -a                                         基于已初始化数据统计重复物料
#   python main.py -a -o "重复物料导出.xlsx"                   统计并导出重复物料
#   python main.py -a -f "导出数据_物料_1110100142.xlsx"       用指定文件统计（不落库）
#   python main.py -c -f "new.xlsx"                            校验新文件，识别已存在物料
#   python main.py -c -f "new.xlsx" -o "已存在的物料.xlsx"      校验并导出已存在物料
#
# 参数说明:
#   -init  必须搭配 -f（基础数据文件），用于初始化基础数据
#   -a     可选搭配 -f（指定数据源文件）和 -o（重复物料输出路径）；都不传则查现有数据
#   -c     必须搭配 -f（待校验文件）；-o 可选，用于输出已存在物料
# """,
#     )
#
#     mode = p.add_mutually_exclusive_group(required=True)
#     mode.add_argument("-init", "--init", action="store_true",
#                       help="加载文件初始化基础数据（必须搭配 -f）")
#     mode.add_argument("-a", "--analyse", action="store_true",
#                       help="执行统计校验（-f、-o 均可选）")
#     mode.add_argument("-c", "--check", action="store_true",
#                       help="check 模式")
#
#     p.add_argument("-f", "--file", metavar="FILE",
#                    help="init 模式：基础数据 Excel 文件；"
#                         "analyse 模式：可选，指定统计用数据文件；"
#                         "check 模式：待校验 Excel 文件")
#     p.add_argument("-o", "--out", metavar="FILE", default=None,
#                    help="analyse 模式：重复物料导出路径；"
#                         "check 模式：已存在物料导出路径；"
#                         "init 模式不可用")
#     return p
#
#
# def validate_args(parser, args):
#     """按模式校验参数组合，不合法时抛 parser.error。"""
#     if args.init:
#         if not args.file:
#             parser.error("-init 模式必须通过 -f 指定基础数据文件")
#         if args.out:
#             parser.error("-init 模式不支持 -o 参数")
#     elif args.check:
#         if not args.file:
#             parser.error("-c 模式必须通过 -f 指定待校验 Excel 文件")
#     elif args.analyse:
#         # -f、-o 都可选，无需额外校验
#         pass
#
#
# def main():
#     parser = build_parser()
#     args = parser.parse_args()
#     validate_args(parser, args)
#     if args.init:
#         init_material(args.file, DB, BASE_TABLE)
#     elif args.analyse:
#         if args.file:
#             init_material(args.file, DB, CHECK_TABLE)
#         analyse_duplicate(DB, export_path=args.out or None)
#     elif args.check:
#         if args.file:
#             init_material(args.file, DB, CHECK_TABLE)
#         check_data(DB, args.out or None)
#     else:
#         parser.error("不支持的操作")
#
#
# if __name__ == '__main__':
#     main()
