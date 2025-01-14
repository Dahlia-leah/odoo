from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    assigned_employee_id = fields.Many2one(
        'hr.employee',
        string="Assigned To",
        domain="[('id', 'in', team_id.member_ids.ids)]",
        help="Only members of the Helpdesk Team can be assigned."
    )

    member_ids = fields.Many2many(
        'hr.employee',
        string="Team Members",
        readonly=True,
        related='team_id.member_ids'
    )

    @api.model
    def create(self, vals):
        ticket = super(HelpdeskTicket, self).create(vals)

        # Find or create the "Helpdesk" project
        helpdesk_project = self.env['project.project'].search([('name', '=', 'Helpdesk')], limit=1)
        if not helpdesk_project:
            helpdesk_project = self.env['project.project'].create({'name': 'Helpdesk'})

        # Create a task in the "Helpdesk" project
        self.env['project.task'].create({
            'name': f"Task for Ticket: {ticket.name}",
            'project_id': helpdesk_project.id,
            'description': ticket.description or "",
            'user_ids': [(6, 0, [ticket.assigned_employee_id.user_id.id])],
            'helpdesk_ticket_id': ticket.id,
        })

        return ticket
