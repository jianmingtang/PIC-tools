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
;	This class is used to load EM fields from PIC data
;-
pro FieldNASA__define
	compile_opt idl2
	data = { Field, path:'', fheader:'', nss:0L, $
		it:0L, dt:0., teti:0., xmax:0., zmax:0., nnx:0L, nnz:0L, $
		time:0., wpewce:0., $
		vxs:ptr_new(), vys:ptr_new(), vzs:ptr_new(), $
		Bx:ptr_new(), By:ptr_new(), Bz:ptr_new(), $
		Ex:ptr_new(), Ey:ptr_new(), Ez:ptr_new(), $
		dns:ptr_new(), xe:ptr_new(), ze:ptr_new(), $
		mass:ptr_new(), q:ptr_new(), dfac:ptr_new(), $
		pxx:ptr_new(), pyy:ptr_new(), pzz:ptr_new(), $
		pxy:ptr_new(), pxz:ptr_new(), pyz:ptr_new() }
end

function FieldNASA::Init, nss, nx, nz, path=path, fheader=fheader
	self.path = path
	self.fheader = fheader
	self.nss = nss
	self.it = lonarr(1)
	self.dt = fltarr(1)
	self.teti = fltarr(1)
	self.xmax = fltarr(1)
	self.zmax = fltarr(1)
	self.nnx = lonarr(1)
	self.nnz = lonarr(1)
	self.time = dblarr(1)
	self.wpewce = fltarr(1)
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
	self.pxx = ptr_new(fltarr(nx,nz,nss))
	self.pyy = ptr_new(fltarr(nx,nz,nss))
	self.pzz = ptr_new(fltarr(nx,nz,nss))
	self.pxy = ptr_new(fltarr(nx,nz,nss))
	self.pxz = ptr_new(fltarr(nx,nz,nss))
	self.pyz = ptr_new(fltarr(nx,nz,nss))
	return, 1
end

function FieldNASA::Update, ftime
	fname = self.path + '/' + self.fheader + '-' + ftime + '.dat'
	openu, id, fname, /f77_unformatted, /get_lun
	readu, id, self.it, self.dt, self.teti, $
		self.xmax, self.zmax, self.nnx, self.nnz, $
		*self.vxs, *self.vys, *self.vzs, $
		*self.Bx, *self.By, *self.Bz, $
		*self.Ex, *self.Ey, *self.Ez, $
		*self.dns,*self.xe,*self.ze,*self.mass,*self.q, $
		self.time, self.wpewce,*self.dfac, $
		*self.pxx, *self.pyy, *self.pzz, $
		*self.pxy, *self.pxz, *self.pyz
	close, id
	return, 1
end

function FieldNASA::Get, var
	if var eq 'vxs' then return, self.vxs else $
	if var eq 'vys' then return, self.vys else $
	if var eq 'vzs' then return, self.vzs else $
	if var eq 'Bx' then return, self.Bx else $
	if var eq 'By' then return, self.By else $
	if var eq 'Bz' then return, self.Bz else $
	if var eq 'Ex' then return, self.Ex else $
	if var eq 'Ey' then return, self.Ey else $
	if var eq 'Ez' then return, self.Ez else $
	if var eq 'xe' then return, self.xe else $
	if var eq 'ze' then return, self.ze else $
	if var eq 'pxx' then return, self.pxx else $
	if var eq 'pyy' then return, self.pyy else $
	if var eq 'pzz' then return, self.pzz else $
	if var eq 'pxy' then return, self.pxy else $
	if var eq 'pxz' then return, self.pxz else $
	if var eq 'pyz' then return, self.pyz else $
	return, 0
end

pro FieldNASA::Print
	print, format='("Field range: x=(",(F8.3),",",(F8.3),' $
		+ '"), z=(",(F8.3),",",(F8.3),")")', $
		(*self.xe)[0],(*self.xe)[-1],(*self.ze)[0],(*self.ze)[-1]
end
