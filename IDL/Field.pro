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
;	This class is used to store field data
;-
pro Field__define
	compile_opt idl2
	data = { Field, nss:0L, it:0L, dt:0., teti:0., $
		xmax:0., zmax:0., nnx:0L, nnz:0L, $
		vxs:ptr_new(), vys:ptr_new(), vzs:ptr_new(), $
		Bx:ptr_new(), By:ptr_new(), Bz:ptr_new(), $
		Ex:ptr_new(), Ey:ptr_new(), Ez:ptr_new(), $
		dns:ptr_new(), xe:ptr_new(), ze:ptr_new(), $
		mass:ptr_new(), q:ptr_new(), dfac:ptr_new(), $
		data2D:ptr_new(), data3D:ptr_new() }
end

function Field::init, fname,nss,nx,nz
	it=lonarr(1)
	dt=fltarr(1)
	teti=fltarr(1)
	xmax=fltarr(1)
	zmax=fltarr(1)
	nnx=lonarr(1)
	nnz=lonarr(1)
	self.nss = nss
	self.vxs = ptr_new(fltarr(nx,nz,nss))
	self.vys = ptr_new(fltarr(nx,nz,nss))
	self.vzs = ptr_new(fltarr(nx,nz,nss))
	self.Bx = ptr_new(fltarr(nx,nz))
	self.By = ptr_new(fltarr(nx,nz))
	self.Bz = ptr_new(fltarr(nx,nz))
	self.Ex = ptr_new(fltarr(nx,nz))
	self.Ey = ptr_new(fltarr(nx,nz))
	self.Ez = ptr_new(fltarr(nx,nz))
	self.dns = ptr_new(fltarr(nx,nz,nss))
	self.xe = ptr_new(fltarr(nx))
	self.ze = ptr_new(fltarr(nz))
	self.mass = ptr_new(fltarr(nss))
	self.q = ptr_new(fltarr(nss))
	self.dfac = ptr_new(fltarr(nss))
	openu, id, fname, /f77_unformatted, /get_lun
	readu, id, it,dt,teti,xmax,zmax,nnx,nnz, $
		*self.vxs,*self.vys,*self.vzs, $
		*self.Bx,*self.By,*self.Bz,*self.Ex,*self.Ey,*self.Ez, $
		*self.dns,*self.xe,*self.ze,*self.mass,*self.q
	close, id
	return, 1
end

function Field::get, var
	if var eq 'Bx' then return, self.Bx else $
	if var eq 'By' then return, self.By else $
	if var eq 'Bz' then return, self.Bz else $
	if var eq 'Ex' then return, self.Ex else $
	if var eq 'Ey' then return, self.Ey else $
	if var eq 'Ez' then return, self.Ez else $
	if var eq 'xe' then return, self.xe else $
	if var eq 'ze' then return, self.ze else $
	return, 0
end

pro Field::print
	print, format='("Field range: x=(",(F8.3),",",(F8.3),' $
		+ '"), z=(",(F8.3),",",(F8.3),")")', $
		(*self.xe)[0],(*self.xe)[-1],(*self.ze)[0],(*self.ze)[-1]
end
