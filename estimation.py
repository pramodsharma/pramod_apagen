from osv import  osv,fields
from datetime import datetime

class Estimation(osv.osv):
    _name='estimation'
    _columns = {
            'creation_date': fields.datetime('Creation Date'),
            'facility':fields.many2one('stock.warehouse','Facility',required='True'),
            'tariff_version':fields.many2one('tariff.versions','Tariff Version'),
            'est':fields.char('EST #'),
            'customer':fields.many2one('res.partner','Customer', required='True'),
            'responsible':fields.many2one('res.users','Responsible', required='True', readonly='True'),
            'inspection_type':fields.many2one('inspection.type','Inspection Type',required='True'),
            'equipment_type':fields.many2one('equipment.type','Equipment Type',required='True'),
            'additional_info':fields.text('Additional Info'),
            'estimation_line':fields.one2many('estimation.line', 'dimension_x', 'Estimation Line'),
            'state': fields.selection([
                ('draft','Draft'),
                ('inspection','Inspection'),
                ('estimation','Estimation'),
                ('awaiting_customer_approval','Awaiting Customer Approval'),
                ('manually_approved','Manually Approved'),
                ('customer_approved','Customer Approved'),
                ('cancelled','Cancelled'),
                ], 'State', readonly=True),
                    }
    _defaults = {  
                 'est': 'EST #',
                 'creation_date':lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'state':'draft',
                 'responsible':lambda obj, cr, uid, context: uid,
        }

    def create(self, cr, uid, vals, context=None):
        if vals.get('est','/')=='/':
            vals['est'] = self.pool.get('ir.sequence').get(cr, uid, 'estimation1') or '/'
        return super(Estimation, self).create(cr, uid, vals, context=context)

    def inspection(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'inspection'})
        return True

    def estimation(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'estimation'})
        print "Written"
        return True

    def estimation_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'draft' })    
        return True  

    def edi(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'draft' })    
        return True
    
    def manually_approved(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'manually_approved' })    
        return True
               
               
    def customer_approved(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'customer_approved' })    
        return True
                   
    def cancelled(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'cancelled' })    
        return True                   
    
    
class EstimationLine(osv.osv):
    _name='estimation.line'
    _columns = {
            'position': fields.many2one('equipment.type','Position'),
            'job_code':fields.many2one('job.codes','Job Code', required='True'),
            'damage_code':fields.many2one('damage.code','Damage Code',required='True'),
            'component_location':fields.many2one('component.location','Component Location'),
            'material':fields.selection([('aluminium','Aluminium'),('steel_carbon','Steel Carbon'),('plywood','Plywood'),('hardwood_plank','Hardwood Plank'),('rubber','Rubber'),('plastic','Plastic '),('no_material','No Material'),('material_unspecified','Material Unspecified')], 'Category'),
            'product':fields.many2one('product.product','Product'),
            'dimension_x':fields.float('Dimension X (in)'),
            'dimension_y':fields.float('Dimension y (in)'),
            'quantity':fields.float('Quantity'),
            'uom':fields.many2one('product.uom.categ','UoM'),
            'unit_price':fields.float('Unit Price'),
            'tax_id': fields.many2many('account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 'Taxes'),
            'subtotal':fields.float('Subtotal'),
                    }
    _defaults={
               'quantity': 1
               }


class EquipmentType(osv.osv):
    _name='equipment.type'
    _columns = {
            'name': fields.char('Name', size=50,required='True'),
            'category':fields.selection([('chassis','Chassis'),('container','Container'),('genset','Reefer'),('reefer','Genset')], 'Category'),
            'positions':fields.many2many('equipment.positions','equipment_positions_equipment_rel','section_code','description','Positions'),
            'description':fields.text('Description'),
                    }

class EquipmentCondition(osv.osv):
    _name='equipment.condition'
    _columns = {
            'name': fields.float('Name', size=50,required='True'),
                    }


class EquipmentPositions(osv.osv):
    _name='equipment.positions'
    _rec_name='section_code'
    _columns = {
            'section_code': fields.char('Section Code', required='True'),
            'description': fields.char('Description'),
            'sequence': fields.integer('Sequence'),
            'job_codes_table':fields.many2many('job.codes','job_codes_position_rel','job_code','description','Job Codes Table'),
                    }


class EquipmentSections(osv.osv):
    _name='equipment.sections'
    _columns = {
            'section_code': fields.char('Section Code', size=50,required='True'),
            'description':fields.char('Description'),
            'sequence':fields.integer('Sequence'),
            'job_codes_table': fields.many2many('job.codes','job_codes_equipment_rel','job_code','description','Job Codes Table'),
                    }
    
    
class InspectionType(osv.osv):
    _name='inspection.type'
    _columns = {
            'name': fields.char('Name',required='True'),
            'description':fields.char('Description',required='True'),
            'default_type':fields.boolean('Default Type '),
            'job_codes':fields.one2many('job.codes', 'inspection_type', 'Jobs Code'),
            #'job_codes':fields.one2many('job.codes', 'job_code', 'Job Codes'),
                    }      
    
    
class JobCodes(osv.osv):
    _name='job.codes'
    _rec_name='job_code'
    _columns = {
            'job_code': fields.char('Job Code',size=60,required='True'),
            'description':fields.char('Description'),
            'sequence':fields.integer('sequence', size=50),
            'component_code':fields.many2one('component.code','Component Code'),
            'repair_code':fields.many2one('repair.code','Repair Code'),
            'damage_codes':fields.many2many('damage.code','damage_job_code_rel','damage_code','description','Damage Codes'),
            'component_location':fields.many2many('component.location','component_location_job_rel','location_name','description','Component Location'),
            'standard_labour_hours':fields.float('Standard Labour (Hours)'),
            'inspection_type':fields.many2one('inspection.type','Inspection Type'),
            'mno':fields.integer('MNO'),
                    }


class DamageCode(osv.osv):
    _name='damage.code'
    _rec_name='damage_code'
    _columns = {
            'damage_code': fields.char('Damage Code', required='True'),
            'description':fields.char('Description'),
                    }

class ComponentCode(osv.osv):
    _name='component.code'
    _rec_name='component_code'
    _columns = {
            'component_code': fields.char('Component Code ',required='True'),
            'description':fields.char('Description'),
                    }
    
class ComponentLocation(osv.osv):
    _name='component.location'
    _rec_name='location_name'
    _columns = {
            'location_name': fields.char('Location Name',required='True'),
            'description':fields.char('Description'),
                    }


class RepairCode(osv.osv):
    _name='repair.code'
    _rec_name='repair_code'
    _columns = {
            'repair_code': fields.char('Repair Code',required='True'),
            'description':fields.char('Description'),
                    }    

class TariffVersions(osv.osv):
    _name='tariff.versions'
    _columns = {
            'name': fields.char('Name',required='True'),
            'start_date':fields.date('Start Date'),
            'end_date':fields.date('End Date'),
                    }  
   