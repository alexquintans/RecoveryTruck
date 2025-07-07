"""combined migration - equipments and operation config

Revision ID: 003
Revises: 002
Create Date: 2025-06-30 20:00:00

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Crie as tabelas base primeiro
    op.create_table(
        'payment_sessions',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', pg.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('service_id', pg.UUID(as_uuid=True), sa.ForeignKey('services.id'), nullable=False),
        sa.Column('customer_name', sa.String(100), nullable=False),
        sa.Column('customer_cpf', sa.String(11), nullable=False),
        sa.Column('customer_phone', sa.String(20), nullable=False),
        sa.Column('consent_version', sa.String(10), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('payment_method', sa.String(20), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('transaction_id', sa.String(100)),
        sa.Column('payment_link', sa.Text),
        sa.Column('webhook_data', pg.JSONB),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'receipts',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('payment_session_id', pg.UUID(as_uuid=True), sa.ForeignKey('payment_sessions.id'), nullable=False, unique=True),
        sa.Column('content', pg.JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'extras',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', pg.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('price', sa.Numeric(10,2), nullable=False),
        sa.Column('category', sa.String(50)),
        sa.Column('stock', sa.Integer, default=0),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'equipments',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', pg.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('service_id', pg.UUID(as_uuid=True), sa.ForeignKey('services.id')),
        sa.Column('type', pg.ENUM('totem', 'panel', 'printer', name='equipment_type', create_type=False), nullable=False),
        sa.Column('identifier', sa.String(100), nullable=False, unique=True),
        sa.Column('location', sa.String(255)),
        sa.Column('status', pg.ENUM('online', 'offline', 'maintenance', name='equipment_status', create_type=False), nullable=False, server_default='online'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('assigned_operator_id', pg.UUID(as_uuid=True), sa.ForeignKey('operators.id')),
    )

    op.create_table(
        'operation_config',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', pg.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('operator_id', pg.UUID(as_uuid=True), sa.ForeignKey('operators.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'operation_config_services',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('operation_config_id', pg.UUID(as_uuid=True), sa.ForeignKey('operation_config.id'), nullable=False),
        sa.Column('service_id', pg.UUID(as_uuid=True), sa.ForeignKey('services.id'), nullable=False),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('duration', sa.Integer, nullable=False),
        sa.Column('price', sa.Numeric(10,2), nullable=False),
        sa.Column('equipment_count', sa.Integer, nullable=False),
    )

    op.create_table(
        'operation_config_equipments',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('operation_config_id', pg.UUID(as_uuid=True), sa.ForeignKey('operation_config.id'), nullable=False),
        sa.Column('equipment_id', pg.UUID(as_uuid=True), sa.ForeignKey('equipments.id'), nullable=False),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('quantity', sa.Integer, nullable=False),
    )

    op.create_table(
        'operation_config_extras',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('operation_config_id', pg.UUID(as_uuid=True), sa.ForeignKey('operation_config.id'), nullable=False),
        sa.Column('extra_id', pg.UUID(as_uuid=True), sa.ForeignKey('extras.id'), nullable=False),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('stock', sa.Integer, nullable=False),
        sa.Column('price', sa.Numeric(10,2), nullable=False),
    )

    # 2. Só depois altere as tabelas existentes
    op.add_column('tickets', sa.Column('payment_session_id', pg.UUID(as_uuid=True), sa.ForeignKey('payment_sessions.id'), nullable=True))
    op.add_column('consents', sa.Column('payment_session_id', pg.UUID(as_uuid=True), sa.ForeignKey('payment_sessions.id'), nullable=True))
    op.drop_constraint('consents_ticket_id_fkey', 'consents', type_='foreignkey')
    op.drop_column('consents', 'ticket_id')
    op.drop_table('payments')

def downgrade():
    op.drop_table('operation_config_extras')
    op.drop_table('operation_config_equipments')
    op.drop_table('operation_config_services')
    op.drop_table('operation_config')
    op.drop_table('extras')
    op.drop_table('receipts')
    op.drop_table('payment_sessions')
    op.drop_table('equipments')
    
    # Recreate old payments table
    op.create_table(
        'payments',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', pg.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('ticket_id', pg.UUID(as_uuid=True), sa.ForeignKey('tickets.id'), nullable=False),
        sa.Column('transaction_id', sa.String(100), nullable=False, unique=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('payment_method', sa.String(20), nullable=False),
        sa.Column('payment_link', sa.Text),
        sa.Column('webhook_data', pg.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
    )
    
    # Revert consents table changes
    op.add_column('consents', sa.Column('ticket_id', pg.UUID(as_uuid=True), sa.ForeignKey('tickets.id'), nullable=True))
    op.drop_constraint('consents_payment_session_id_fkey', 'consents', type_='foreignkey')
    op.drop_column('consents', 'payment_session_id')
    
    # Remove payment_session_id column from tickets table
    op.drop_column('tickets', 'payment_session_id')
    
    # Drop ENUMs
    equipment_type = pg.ENUM('totem', 'panel', 'printer', name='equipment_type', create_type=False)
    equipment_type.drop(op.get_bind(), checkfirst=True)
    
    equipment_status = pg.ENUM('online', 'offline', 'maintenance', name='equipment_status', create_type=False)
    equipment_status.drop(op.get_bind(), checkfirst=True) 