from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'

    name = fields.Char(string='Ticket Name', required=True)
    description = fields.Text(string='Description')
    team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team')
    assigned_to = fields.Many2one('res.users', string='Assigned To', domain="[('id', 'in', team_member_ids)]")
    team_member_ids = fields.Many2many(related='team_id.member_ids', string='Team Members')
    task_id = fields.Many2one('project.task', string='Related Task')

    @api.model
    def create(self, vals):
        ticket = super(HelpdeskTicket, self).create(vals)
        if ticket.team_id:
            task = self.env['project.task'].create({
                'name': f"Task for Ticket: {ticket.name}",
                'description': ticket.description,
                'project_id': self.env.ref('project.project_helpdesk').id,  # Assuming you have a default helpdesk project
                'user_id': ticket.assigned_to.id,
            })
            ticket.write({'task_id': task.id})
        return ticket

