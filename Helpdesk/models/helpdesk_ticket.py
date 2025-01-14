from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    assigned_user_id = fields.Many2one(
        'res.users',
        string="Assigned To",
        domain="[('id', 'in', member_ids)]",
        help="Only members of the Helpdesk Team can be assigned."
    )

    member_ids = fields.Many2many(
        related='team_id.member_ids',
        domain="[('id', 'in', employee_id)]",
        string="Team Members",
        readonly=True
    )

    @api.model
    def create(self, vals):
        ticket = super(HelpdeskTicket, self).create(vals)

        # Find or create the "Helpdesk" project
        helpdesk_project = self.env['project.project'].search([('name', '=', 'Helpdesk')], limit=1)
        if not helpdesk_project:
            helpdesk_project = self.env['project.project'].create({'name': 'Helpdesk'})

        # Create a task in the "Helpdesk" project
        task = self.env['project.task'].create({
            'name': f"Task for Ticket: {ticket.name}",
            'project_id': helpdesk_project.id,
            'description': ticket.description or "",
            'user_ids': [(6, 0, [ticket.assigned_user_id.id])],  # Corrected field name
            'helpdesk_ticket_id': ticket.id,
        })


        return ticket
