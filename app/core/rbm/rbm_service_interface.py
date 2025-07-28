from abc import ABC, abstractmethod
from .messageTo import MessageTo

class RBMServiceInterface(ABC):
    @abstractmethod
    def send_message(self, message: MessageTo):
        """Retrieve an RBM by its ID."""
        pass

    @abstractmethod
    def rbm_message(self, message):
        """Send a message to an RBM."""
        pass

    @abstractmethod
    def StandaloneCard(self, orientation, title, description, suggestions,image_url, size):
        """Send a message to an RBM by its MSISDN."""
        pass