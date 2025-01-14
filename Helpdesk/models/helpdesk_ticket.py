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
        string="Team Members",
        readonly=True
    )

    @api.model
    def create(self, vals):
        ticket = super(HelpdeskTicket, self).create(vals)

        # Auto-create task for the new Helpdesk ticket
        if ticket.team_id and ticket.team_id.project_id:
            self.env['project.task'].create({
                'name': f"Task for Ticket: {ticket.name}",
                'project_id': ticket.team_id.project_id.id,
                'description': ticket.description or "",
                'assigned_user_id': ticket.assigned_user_id.id,  # Updated field name
                'helpdesk_ticket_id': ticket.id,
            })

        return ticket
