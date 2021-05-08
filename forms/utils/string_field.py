from wtforms import StringField


class StringField(StringField):
    def validate(self, *args, **kwargs):
        if type(self.data) == str:
            self.data = self.data.strip()
        return super().validate(*args, **kwargs)
