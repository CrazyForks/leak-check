import re

from pydantic import BaseModel, Field, model_validator


class ModelRequestQuery(BaseModel):
    q: str

    type: str | None = None  # 👈 自动识别出来

    @model_validator(mode="before")
    @classmethod
    def validate_and_detect(cls, values):
        q_ = values.get("q")
        if not q_ or not q_.strip():
            raise ValueError("q 不能为空")

        q_ = q_.strip()
        cleaned = re.sub(r"[ \-\(\)]", "", q_)

        cn_phone_pattern = r"^1\d{10}$"
        intl_phone_pattern = r"^\+\d{6,15}$"
        phone_pattern = rf"(?:{cn_phone_pattern})|(?:{intl_phone_pattern})"

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        mainland_id_pattern = r"^\d{17}[\dXx]$"
        taiwan_id_pattern = r"^[A-Z][12]\d{8}$"
        id_pattern = rf"(?:{mainland_id_pattern})|(?:{taiwan_id_pattern})"

        qq_pattern = rf"^(?!{phone_pattern}$)\d{{5,11}}$"

        # =========================
        # 👉 直接产出类型
        # =========================
        if re.fullmatch(phone_pattern, cleaned):
            values["type"] = "phone"
        elif re.fullmatch(email_pattern, q_):
            values["type"] = "email"
        elif re.fullmatch(id_pattern, cleaned):
            values["type"] = "id"
        elif re.fullmatch(qq_pattern, cleaned):
            values["type"] = "qq"
        else:
            raise ValueError("q 必须是身份证号 | 手机号 | 邮箱 | QQ 号之一")

        # 顺便统一清洗后的值（可选）
        values["q"] = cleaned

        return values