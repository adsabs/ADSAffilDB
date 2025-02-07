from adsputils import ADSCelery


class ADSAffilDBCelery(ADSCelery):
    def __init__(self, app_name, *args, **kwargs):
        ADSCelery.__init__(self, app_name, *args, **kwargs)
