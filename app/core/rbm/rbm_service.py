from .rbm_repository_interface import RBMRepositoryInterface
from .rbm_service_interface import RBMServiceInterface
from .messageTo import MessageTo
from rcs_business_messaging import messages


class RBMService(RBMServiceInterface):
    def __init__(self, repository: RBMRepositoryInterface):
        self.repository = repository

    def send_message(self, message: MessageTo):
        """Send a message using the RBM repository."""
        return self.repository.send_message(message)
    
    def rbm_message(self, message):
        message = messages.TextMessage(message)
        return message
        
    
    def StandaloneCard(self, orientation, title, description, suggestions,image_url, size):
        suggestions_list_rbm=[]
        for clave,suggestion in suggestions.items():
            print(f"🔔 Agregando sugerencia: {clave} -> {suggestion}")
            suggestions_list_rbm.append(messages.SuggestedReply(clave, suggestion))
        
        rich_card = self.repository.StandaloneCard(orientation,
                                        title,
                                        description,
                                        suggestions_list_rbm,
                                        image_url,
                                       size)
        return rich_card


