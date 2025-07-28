from .rbm_repository_interface import RBMRepositoryInterface
from .messageTo import MessageTo

from rcs_business_messaging import rbm_service
from rcs_business_messaging import messages


class RBMRepository(RBMRepositoryInterface):
    def __init__(self,AGENT_ID):
        rbm_service.init(AGENT_ID)
        
        self.rbms = messages.MessageCluster()

    def send_message(self,message: MessageTo):
        """Retrieve an RBM by its ID."""
        return self.rbms.append_message(message.get_message()).send_to_msisdn(message.get_msisdn())
    
    def rbm_message(self, message):
        """Send a message to an RBM."""
        pass
    def StandaloneCard(self, orientation, title, description,suggestions, image_url, size):
        rich_card=messages.StandaloneCard(orientation,
                                        title,
                                        description,
                                        suggestions,
                                        image_url,
                                        None,
                                        None,
                                       size)
        return rich_card