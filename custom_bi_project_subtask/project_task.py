# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from odoo import models, fields, api, _

class project_task(models.Model):
    _inherit = "project.task"

    '''@api.model
    def default_get(self, fields):
        rec = super(project_task, self).default_get(fields)
        task = self._context.get('active_id')
        task_bro=self.browse(task)
        rec.update({'project_id': task_bro.project_id.id,
                    'user_id': task_bro.user_id.id})
        return rec'''


    parent_id = fields.Many2one('project.task','Sub task')
    task_sub_ids = fields.One2many('project.task', 'parent_id', 'SubTasks')

    @api.model
    def create(self,vals):
        
        if vals.get('parent_id'):
            task_id = self.browse(vals.get('parent_id'))
            vals.update({'project_id':task_id.project_id.id,})
        task = super(project_task, self).create(vals)
        return task



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
