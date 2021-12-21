from common_amirainvest_com.utils.exceptions.base import AmiraInvestExceptionBase


class CompositePrimaryKeyError(AmiraInvestExceptionBase):
    def __init__(self, model, primary_keys):
        self.message = f"{model} with has a composite primary key ({primary_keys}) & needs custom sqlalchemy updates."
        super().__init__(self.message)

    def __str__(self):
        return self.message
