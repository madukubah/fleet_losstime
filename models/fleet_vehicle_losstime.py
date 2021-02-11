# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time
import datetime
from dateutil.relativedelta import relativedelta

# import logging
# _logger = logging.getLogger(__name__)
class FleetVehicle(models.Model):
	_inherit = 'fleet.vehicle'
	losstime_count = fields.Integer(compute="_compute_count_all", string='losstime')

	@api.multi
	def losstime_return_action_to_open(self):
		""" This opens the xml view specified in xml_id for the current vehicle """
		self.ensure_one()
		xml_id = self.env.context.get('xml_id')
		if xml_id:
			res = self.env['ir.actions.act_window'].for_xml_id('fleet_losstime', xml_id)
			res.update(
				context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
				domain=[('vehicle_id', '=', self.id)]
			)
			return res
		return False
	
	@api.multi
	def _compute_count_all(self):
		super(FleetVehicle, self )._compute_count_all()
		VehicleLosstime = self.env['fleet.vehicle.losstime']
		for record in self:
			losstimes = VehicleLosstime.search([('vehicle_id', '=', record.id)])
			record.losstime_count = sum([ losstime.hour for losstime in losstimes ])

class FleetVehicleLosstime(models.Model):
    _name = "fleet.vehicle.losstime"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "date desc"
    
    name = fields.Char(compute='_compute_name', store=True)
    date = fields.Date('Date', help='',  default=fields.Datetime.now )
    vehicle_id  = fields.Many2one('fleet.vehicle', 'Vehicle', required=True)
    tag_ids = fields.Many2many('fleet.vehicle.tag', 'vehicle_losstime_vehicle_tag_rel', 'vehicle_losstime_tag_id', 'tag_id', 'Tags', store=True, compute="_compute_tag_ids")
    driver_id	= fields.Many2one('res.partner', string='Driver' )
    shift = fields.Selection([
        ( "1" , '1'), 
        ( "2" , '2'), 
        ], string='Shift', index=True, required=True )
    losstime_type = fields.Selection([
        ('breakdown', 'Breakdown'), 
		('slippery', 'Slippery'),
		('rainy', 'Rainy'),
		('no_operator', 'No Operator'),
        ], string='Losstime type', index=True, required=True )
    start_datetime = fields.Datetime('Start Date Time', help='',  default=fields.Datetime.now )
    end_datetime = fields.Datetime('End Date Time', help='' )
    minutes = fields.Float('Minutes', readonly=True, compute="_compute_hour" )
    hours = fields.Float('Hours', readonly=True, compute="_compute_hour" )

    start = fields.Float('Start Hourmeter')
    end = fields.Float('End Hourmeter')
    hour = fields.Float('Hourmeter Value', readonly=True, compute="_compute_hour" )

    remarks = fields.Char( String="Remarks", store=True)

    @api.depends( 'vehicle_id')
    def _compute_tag_ids(self):
        for record in self:
            record.update({
                    'tag_ids': [( 6, 0, record.vehicle_id.tag_ids.ids )],
                })

    @api.onchange( 'date' )
    def _set_date(self):
        for record in self:
            record.start_datetime = record.date
            record.end_datetime = record.date
            
    @api.depends( 'date')
    def _compute_name(self):
        for record in self:
            name = record.vehicle_id.name
            if not name:
                name = record.date
            elif record.date:
                name += ' / ' + record.date
            self.name = name
    
    @api.onchange('vehicle_id')	
    def _change_vehicle_id(self):
        for record in self:
            record.driver_id = record.vehicle_id.driver_id
    
    @api.depends('start_datetime', 'end_datetime', 'start', 'end' )
    def _compute_hour(self):
        for record in self:
            #compute end date
            if record.start_datetime and record.end_datetime :
                start = datetime.datetime.strptime(record.start_datetime, '%Y-%m-%d %H:%M:%S')
                ends = datetime.datetime.strptime(record.end_datetime, '%Y-%m-%d %H:%M:%S')
                diff = relativedelta(ends, start)
                record.minutes = diff.minutes + ( diff.hours * 60 )
                record.hours = diff.hours

                record.hour = record.end - record.start
