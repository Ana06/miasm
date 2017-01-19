#-*- coding:utf-8 -*-

from miasm2.expression.expression import *
from miasm2.ir.ir import ir, irbloc, AssignBlock
from miasm2.ir.analysis import ira
from miasm2.arch.mips32.sem import ir_mips32l, ir_mips32b
from miasm2.arch.mips32.regs import *
from miasm2.core.asmbloc import expr_is_int_or_label, expr_is_label

class ir_a_mips32l(ir_mips32l, ira):
    def __init__(self, symbol_pool=None):
        ir_mips32l.__init__(self, symbol_pool)
        self.ret_reg = self.arch.regs.V0


    # for test XXX TODO
    def set_dead_regs(self, b):
        pass

    def pre_add_instr(self, block, instr, irb_cur, ir_blocks_all, gen_pc_updt):
        # Avoid adding side effects, already done in post_add_bloc
        return irb_cur

    def post_add_bloc(self, bloc, ir_blocs):
        ir.post_add_bloc(self, bloc, ir_blocs)
        for irb in ir_blocs:
            pc_val = None
            lr_val = None
            for assignblk in irb.irs:
                pc_val = assignblk.get(PC, pc_val)
                lr_val = assignblk.get(RA, lr_val)

            if pc_val is None or lr_val is None:
                continue
            if not expr_is_int_or_label(lr_val):
                continue
            if expr_is_label(lr_val):
                lr_val = ExprInt32(lr_val.name.offset)

            l = bloc.lines[-2]
            if lr_val.arg != l.offset + 8:
                raise ValueError("Wrong arg")

            # CALL
            lbl = bloc.get_next()
            new_lbl = self.gen_label()
            irs = self.call_effects(pc_val, l)
            irs.append(AssignBlock([ExprAff(self.IRDst,
                                            ExprId(lbl, size=self.pc.size))]))
            nbloc = irbloc(new_lbl, irs)
            nbloc.lines = [l] * len(irs)
            self.blocs[new_lbl] = nbloc
            irb.dst = ExprId(new_lbl, size=self.pc.size)

    def get_out_regs(self, b):
        return set([self.ret_reg, self.sp])

    def sizeof_char(self):
        return 8

    def sizeof_short(self):
        return 16

    def sizeof_int(self):
        return 32

    def sizeof_long(self):
        return 32

    def sizeof_pointer(self):
        return 32



class ir_a_mips32b(ir_mips32b, ir_a_mips32l):
    def __init__(self, symbol_pool=None):
        ir_mips32b.__init__(self, symbol_pool)
        self.ret_reg = self.arch.regs.V0
