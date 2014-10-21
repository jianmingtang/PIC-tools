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
;	This class is used to load particle distibution data
;-
pro ParticleDistribution__define
	compile_opt idl2
	data = { ParticleDistribution, nss:0L, grid:0L, $
		axes:ptr_new(), bin:ptr_new(), ic:ptr_new(), $
		fxyz:ptr_new(), fxy:ptr_new(), fxz:ptr_new(), fyz:ptr_new(), $
		vxa:ptr_new(), vya:ptr_new(), vza:ptr_new(), $
		data2D:ptr_new(), dataCUT:ptr_new(), dataR:ptrarr(3), $
		data3D:ptr_new() }
end

function ParticleDistribution::init, fname, nss, grid
	self.nss = nss
	self.grid = grid
	self.axes = ptr_new(fltarr(grid,nss))
	self.bin = ptr_new(fltarr(4))
	self.ic = ptr_new(lonarr(nss))
	self.fxyz = ptr_new(fltarr(grid,grid,grid,nss))
	self.fxy = ptr_new(fltarr(grid,grid,nss))
	self.fxz = ptr_new(fltarr(grid,grid,nss))
	self.fyz = ptr_new(fltarr(grid,grid,nss))
	self.vxa = ptr_new(fltarr(nss))
	self.vya = ptr_new(fltarr(nss))
	self.vza = ptr_new(fltarr(nss))
	openu, id, fname, /f77_unformatted, /get_lun
	readu, id, *self.axes,*self.bin,*self.ic, *self.fxyz, $
		*self.fxy,*self.fxz,*self.fyz,*self.vxa,*self.vya,*self.vza
	close, id
	return, 1
end

function ParticleDistribution::get, var
	if var eq 'axes' then return, *self.axes else $
	if var eq 'fxyz' then return, *self.fxyz else $
	if var eq 'fxy' then return, *self.fxy else $
	if var eq 'fxz' then return, *self.fxz else $
	if var eq 'fyz' then return, *self.fyz else $
	if var eq 'add3D' then return, *self.data3D else $
	if var eq 'add2D' then return, *self.data2D else $
	if var eq 'addR' then return, self.dataR else $
	return, 0
end

pro ParticleDistribution::print
	print, format='("Bin location: x=(",(F6.3),",",(F6.3),' $
		+ '"), z=(",(F6.3),",",(F6.3),")")', *self.bin
;	print, *self.ic
end

;+
;  Make a 2D cut perpendicular to 'dir' from rmin to rmax
;-
pro ParticleDistribution::cut, dir, rmin, rmax
	self.dataCUT = ptr_new(fltarr(self.grid,self.grid,self.nss))
	if dir eq 'x' then $
		*self.dataCUT = total((*self.fxyz)[rmin:rmax,*,*,*],1)
	if dir eq 'y' then $
		*self.dataCUT = total((*self.fxyz)[*,rmin:rmax,*,*],2)
	if dir eq 'z' then $
		*self.dataCUT = total((*self.fxyz)[*,*,rmin:rmax,*],3)
end

;+
;  Sum 2D cut data over species in sps
;-
pro ParticleDistribution::add2D, sps
	self.data2D = ptr_new(fltarr(self.grid,self.grid))
	foreach i, sps do begin
		*self.data2D += (*self.dataCUT)[*,*,i]
	endforeach
end

;+
;  Sum reduced 2D data over species in sps
;-
pro ParticleDistribution::addR, sps
	for i = 0, 2 do begin
		self.dataR[i] = ptr_new(fltarr(self.grid,self.grid))
	endfor
	foreach i, sps do begin
		*(self.dataR[0]) += (*self.fxy)[*,*,i]
		*(self.dataR[1]) += (*self.fxz)[*,*,i]
		*(self.dataR[2]) += (*self.fyz)[*,*,i]
	endforeach
end

;+
;  Sum 3D data over species in sps
;-
pro ParticleDistribution::add3D, sps
	self.data3D = ptr_new(fltarr(self.grid,self.grid,self.grid))
	foreach i, sps do begin
		*self.data3D += (*self.fxyz)[*,*,*,i]
	endforeach
end
