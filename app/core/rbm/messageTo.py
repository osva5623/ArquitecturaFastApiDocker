class MessageTo:

    def get_message(self):
        """Return the message to be sent."""
        return self.message

    def get_msisdn(self):
        """Return the MSISDN to send the message to."""
        return self.msisdn
    
    def set_message(self, message):
        """Set the message to be sent."""
        self.message = message

    def set_msisdn(self, msisdn):
        """Set the MSISDN to send the message to."""
        self.msisdn = msisdn