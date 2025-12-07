import json
from models.asset import Asset

class Portfolio:
    def __init__(self, cartera_file):
        self.cartera_file = cartera_file
        self.assets = self.load_assets()

    def load_assets(self):
        try:
            with open(self.cartera_file, 'r') as f:
                data = json.load(f)
                return [Asset.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_assets(self):
        with open(self.cartera_file, 'w') as f:
            json.dump([asset.to_dict() for asset in self.assets], f, indent=4)

    def add_asset(self, asset):
        self.assets.append(asset)
        self.save_assets()

    def update_asset(self, symbol, updated_asset):
        for i, asset in enumerate(self.assets):
            if asset.simbolo == symbol:
                self.assets[i] = updated_asset
                self.save_assets()
                return True
        return False

    def delete_asset(self, symbol):
        self.assets = [asset for asset in self.assets if asset.simbolo != symbol]
        self.save_assets()

    def get_all_assets(self):
        return self.assets

    def get_asset_by_symbol(self, symbol):
        for asset in self.assets:
            if asset.simbolo == symbol:
                return asset
        return None
