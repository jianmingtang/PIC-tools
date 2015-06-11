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
	data = { Field, path:'', $
		xmax:0., zmax:0., nnx:0L, nnz:0L, $
		Bx:ptr_new(), By:ptr_new(), Bz:ptr_new(), $
		Ex:ptr_new(), Ey:ptr_new(), Ez:ptr_new(), $
		data2D:ptr_new(), data3D:ptr_new() }
end

function FieldLANL::Init, nss, nx, nz, path=''
	self.path = path
	self.Bx = ptr_new(fltarr(nx,nz))
	self.By = ptr_new(fltarr(nx,nz))
	self.Bz = ptr_new(fltarr(nx,nz))
	self.Ex = ptr_new(fltarr(nx,nz))
	self.Ey = ptr_new(fltarr(nx,nz))
	self.Ez = ptr_new(fltarr(nx,nz))
	return, 1
end

function FieldLANL::Update, ftime
	xmax=fltarr(1)
	zmax=fltarr(1)
	nnx=lonarr(1)
	nnz=lonarr(1)
	fieldarr = fltarr(self.nx, self.nz)
	fname = self.path + '/' + 'Bx.gda'
	openr, id, fname, /f77_unformatted, /get_lun
	self.Bx = assoc(id, fieldarr)

	return, 1
end

function FieldLANL::Get, var
	if var eq 'Bx' then return, self.Bx else $
	if var eq 'By' then return, self.By else $
	if var eq 'Bz' then return, self.Bz else $
	if var eq 'Ex' then return, self.Ex else $
	if var eq 'Ey' then return, self.Ey else $
	if var eq 'Ez' then return, self.Ez else $
	return, 0
end

pro FieldLANL::Print
	print, format='("Field range: x=(",(F8.3),",",(F8.3),' $
		+ '"), z=(",(F8.3),",",(F8.3),")")', $
		(*self.xe)[0],(*self.xe)[-1],(*self.ze)[0],(*self.ze)[-1]
end
