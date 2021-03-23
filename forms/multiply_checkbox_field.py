from wtforms import Field


class MultiplyCheckboxField(Field):
    def __init__(self, prefix_id, label=None, **kwargs):
        super().__init__(label=label, **kwargs)
        self.choices = []
        self.checked = []
        self.prefix_id = prefix_id
