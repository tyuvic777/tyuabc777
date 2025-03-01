import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.eth_url = os.getenv('ETH_URL', 'http://localhost:8545')
        self.logger = logging.getLogger(__name__)

    def reward_patient(self, patient_id, amount, reason, role='admin', name='Admin'):
        """
        Reward a patient with tokens, ensuring role-specific messages.
        
        Args:
            patient_id (str): Patient ID
            amount (float): Reward amount
            reason (str): Reason for reward
            role (str): User role (default: admin)
            name (str): User name (default: Admin)
        
        Returns:
            dict: Reward result with role-specific message
        """
        try:
            response = requests.post(f'{self.eth_url}/reward', json={
                'from': 'admin_wallet', 'to': patient_id, 'value': amount
            })
            response.raise_for_status()
            blockchain_client = BlockchainClient()  # Assume initialized elsewhere
            blockchain_client.reward_patient(patient_id, amount, reason)
            message = self.get_role_message(role, "patient reward", True, name)
            self.logger.info(f"Patient {patient_id} rewarded {amount} tokens - {message}")
            return {"message": message, "data": response.json()}
        except Exception as e:
            self.logger.error(f"Reward error: {e} - {self.get_role_message(role, 'patient reward', False, name)}")
            raise Exception(self.get_role_message(role, "patient reward", False, name))

    def get_role_message(self, role, feature, success=True, name=None):
        """
        Generate role-specific, user-friendly messages.
        
        Args:
            role (str): User role (admin, doctor, patient)
            feature (str): Feature or action being performed
            success (bool): Whether the action succeeded
            name (str, optional): User name, defaults to role
        
        Returns:
            str: Formatted message
        """
        name = name or role.capitalize()
        messages = {
            'admin': {
                True: f"Thank you, Admin! Your action on {feature} has been completed successfully.",
                False: f"Sorry, Admin, we couldn’t process your {feature} request. Please try again or contact support."
            },
            'doctor': {
                True: f"Great job, Doctor! Your update to {feature} was successful.",
                False: f"Oops, Doctor, we encountered an issue with your {feature}. Please try again later or reach out to support."
            },
            'patient': {
                True: f"Thank you, {name}! Your {feature} has been updated successfully.",
                False: f"Sorry, {name}, we couldn’t complete your {feature} request. Please try again or contact our support team."
            }
        }
        return messages[role][success]

    # [Other methods (reward_doctor, transfer_tokens) with role-specific messages, full version in ZIP]