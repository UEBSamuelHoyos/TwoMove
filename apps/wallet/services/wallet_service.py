# wallet/services/wallet_service.py
from ..models import Wallet

class WalletService:
    @staticmethod
    def obtener_o_crear_wallet(usuario):
        wallet, _ = Wallet.objects.get_or_create(usuario=usuario)
        return wallet

    @staticmethod
    def agregar_saldo(usuario, monto, descripcion="Recarga de saldo"):
        wallet = WalletService.obtener_o_crear_wallet(usuario)
        wallet.agregar_saldo(monto, descripcion)
        return wallet.balance

    @staticmethod
    def descontar_saldo(usuario, monto, descripcion="Pago de servicio"):
        wallet = WalletService.obtener_o_crear_wallet(usuario)
        wallet.descontar_saldo(monto, descripcion)
        return wallet.balance
