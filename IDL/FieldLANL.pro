;
;    Copyright (C) 2014  Jian-Ming Tang <jmtang@mailaps.org>
;
;    This program is free software: you can redistribute it and/or modify
;    it under the terms of the GNU General Public License as published by
;    the Free Software Foundation, either version 3 of the License, or
;    (at your option) any later version.
;
;    This program is distributed in the hope that it will be useful,
;    but WITHOUT ANY WARRANTY; without even the implied warranty of
;    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;    GNU General Public License for more details.
;
;    You should have received a copy of the GNU General Public License
;    along with this program.  If not, see <http://www.gnu.org/licenses/>.
;


;+
;	This class is used to load EM fields from LANL PIC data
;-
pro FieldLANL__define
	compile_opt idl2
	data = { FieldLANL, path:'', nx:0L, ny:0L, nz:0L, $
			xmax:0., ymax:0., zmax:0. data:ptr_new() }
end

function FieldLANL::init, path
	self.path = path
	infofile = path+'/info'
	; open binary file for problem description 
	if ( file_test(infofile) eq 1 ) then begin
   		print," *** Found Data Information File ***"
	endif else begin
		print," *** ERROR: File info is missing ***"
	endelse
	nx = 0L
	ny = 0L
	nz = 0L
	xmax = 0.
	ymax = 0.
	zmax = 0.
	openr, id, infofile, /f77_unformatted, /get_lun
	readu, id, nx, ny, nz
	readu, id, xmax, ymax, zmax
	close, id
	self.nx = nx
	self.ny = ny
	self.nz = nz
	self.xmax = xmax
	self.ymax = ymax
	self.zmax = zmax
	self.data = ptr_new(fltarr(nx,nz))
	print, nx, ny, nz
	return, 1
end

function FieldLANL::draw, var

	draw_field_2D, var, *self.data, [0,self.xmax], [0,self.zmax]
	return, 1
end


function FieldLANL::get, var, time
	nx = self.nx
	nz = self.nz
	fstruct = { data:fltarr(nx,nz),time:0.0,it:0L }
	fname = self.path + '/' + var + '.gda'
	openr, id, fname, /f77_unformatted, /get_lun
	field = assoc(id, fstruct)
	*self.data = (field[time]).data
	close, id
	return, res
end

pro FieldLANL::print
	print, format='("Field range: x=(",(F8.3),",",(F8.3),' $
		+ '"), z=(",(F8.3),",",(F8.3),")")', $
		0,self.xmax,0,self.zmax
end
