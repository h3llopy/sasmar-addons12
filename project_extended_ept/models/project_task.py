# -*- coding: utf-8 -*-
from odoo import models,api,fields

class ProjectTask(models.Model):
    _inherit = "project.task"
    
    description = fields.Text('Description')
    parent_id = fields.Many2one('project.task','Sub task')
    task_sub_ids = fields.One2many('project.task', 'parent_id', 'SubTasks')
    
    @api.model
    def create(self,vals):
        if vals.get('parent_id'):
            task_id = self.browse(vals.get('parent_id'))
            vals.update({'project_id':task_id.project_id.id,})
        task = super(ProjectTask, self).create(vals)
        return task