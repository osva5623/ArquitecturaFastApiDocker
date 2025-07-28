from abc import ABC, abstractmethod
from .messageTo import MessageTo


class RBMRepositoryInterface(ABC):
    @abstractmethod
    def send_message(self,message: MessageTo):
        """Send a message to an RBM by its ID."""
        pass
    @abstractmethod
    def rbm_message(self, message):
        """Send a message to an RBM."""
        pass
    @abstractmethod
    def StandaloneCard(self, orientation, title, description,suggestions, image_url, size):
        """Send a message to an RBM by its MSISDN."""
        pass