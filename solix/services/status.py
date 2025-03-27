"""
   Copyright 2025 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import typing


from util import Device
from api import api
from util import conf


async def handle_status(device: Device, anker_solix_api: api.AnkerSolixApi, *args, **kwargs) -> typing.Dict:
    id = device.id.removeprefix(conf.Discovery.device_id_prefix)
    values = anker_solix_api.devices[id]
    if device.type == conf.Senergy.dt_solarbank:
        site = anker_solix_api.sites[values['site_id']]
        return {
            "battery_soc": float(values['battery_soc']),
            "battery_capacity": float(values['battery_capacity']),
            "battery_energy": float(values['battery_energy']),
            "charging_power": float(values['charging_power']),
            "power_unit": values['power_unit'],
            "charging_status": float(values['charging_status']),
            "charging_status_desc": values['charging_status_desc'],
            "status": float(values['status']),
            "status_desc": values['status_desc'],
            "input_power": float(values['input_power']),
            "output_power": float(values['output_power']),
            "sub_package_num": values['sub_package_num'],
            "output_cutoff_data": values['output_cutoff_data'],
            "bat_charge_power": float(values['bat_charge_power']),
            "set_output_power": float(values['set_output_power']),
            "set_system_output_power": float(values['set_system_output_power']),
            "data_valid": values['data_valid'],
            "solarbank_count": values['solarbank_count'],
            "solar_power_1": float(values['solar_power_1']),
            "solar_power_2": float(values['solar_power_2']),
            "solar_power_3": float(values['solar_power_3']),
            "solar_power_4": float(values['solar_power_4']),
            "ac_power": float(values['ac_power']),
            "to_home_load": float(values['to_home_load']),
            "pei_heating_power": float(values['pei_heating_power']),
            "kwh": float(site['statistics'][0]['total']),
            "kg": float(site['statistics'][1]['total']),
            "EUR": float(site['statistics'][2]['total']),
            "energy_details": {
                "today": {
                    "battery_discharge": float(site['energy_details']['today']['battery_discharge']),
                    "ac_socket": float(site['energy_details']['today']['ac_socket']),
                    "battery_to_home": float(site['energy_details']['today']['battery_to_home']),
                    "grid_to_battery": float(site['energy_details']['today']['grid_to_battery']),
                    "home_usage": float(site['energy_details']['today']['home_usage']),
                    "grid_to_home": float(site['energy_details']['today']['grid_to_home']),
                    "smartplugs_total": float(site['energy_details']['today']['smartplugs_total']),
                    "solar_production_pv1": float(site['energy_details']['today']['solar_production_pv1']),
                    "solar_production_pv2": float(site['energy_details']['today']['solar_production_pv2']),
                    "solar_production_pv3": float(site['energy_details']['today']['solar_production_pv3']),
                    "solar_production_pv4": float(site['energy_details']['today']['solar_production_pv4']),
                    "solar_production": float(site['energy_details']['today']['solar_production']),
                    "battery_charge": float(site['energy_details']['today']['battery_charge']),
                    "solar_to_grid": float(site['energy_details']['today']['solar_to_grid']),
                    "battery_percentage": float(site['energy_details']['today']['battery_percentage']),
                    "solar_percentage": float(site['energy_details']['today']['solar_percentage']),
                    "other_percentage": float(site['energy_details']['today']['other_percentage']),
                }
            }
        }
    elif device.type == conf.Senergy.dt_plug:
        return {
            "current_power": float(values['current_power']),
            "energy_today": float(values['energy_today']),
            "energy_last_period": float(values['energy_last_period']),
            "status": float(values['status']),
            "status_desc": values['status_desc'],
            "err_code": values['err_code'],
        }
    else:
        raise f"Status not implemented for device type {device.type}"
