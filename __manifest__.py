# -*- coding: utf-8 -*-

{
    'name': 'Fleet Vehicle Losstime',
    'version': '1.0',
    'author': 'Technoindo.com',
    'category': 'Fleet',
    'depends': [
        'fleet',
    ],
    'data': [
        'views/menu.xml',
        "views/fleet_vehicle_losstime.xml",
        "views/fleet.xml",

        "security/ir.model.access.csv",
    ],
    'qweb': [
        # 'static/src/xml/cashback_templates.xml',
    ],
    'demo': [
        # 'demo/sale_agent_demo.xml',
    ],
    "installable": True,
	"auto_instal": False,
	"application": False,
}
