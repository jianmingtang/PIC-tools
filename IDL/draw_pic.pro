;
;    draw_dist.pro:
;       Draw particle distribution data in 2D and 3D formats.
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
;	Description: This class is used to store data in ndarray from
;	a NASA PIC data file. Methods for data slicing and summation are provided.
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
	if var eq 'axes' then return, self.axes else $
	if var eq 'fxyz' then return, self.fxyz else $
	if var eq 'fxy' then return, self.fxy else $
	if var eq 'fxz' then return, self.fxz else $
	if var eq 'fyz' then return, self.fyz else $
	if var eq 'add3D' then return, self.data3D else $
	if var eq 'add2D' then return, self.data2D else $
	if var eq 'addR' then return, self.dataR else $
	return, 0
end

pro ParticleDistribution::print
	print, format='("Bin location: x=(",(F6.3),",",(F6.3),' $
		+ '"), z=(",(F6.3),",",(F6.3),")")', *self.bin
	print, *self.ic
end

pro ParticleDistribution::cut, p
end

pro ParticleDistribution::add2D, sps
	self.data2D = ptr_new(fltarr(self.grid,self.grid))
	foreach i, sps do begin
		*self.data2D += (*self.dataCUT)[*,*,i]
	endforeach
end

pro ParticleDistribution::addR, sps
	self.dataR[*] = ptr_new(fltarr(self.grid,self.grid))
	foreach i, sps do begin
		*(self.dataR[0]) += (*self.fxy)[*,*,i]
		*(self.dataR[1]) += (*self.fxz)[*,*,i]
		*(self.dataR[2]) += (*self.fyz)[*,*,i]
	endforeach
end

pro ParticleDistribution::add3D, sps
	self.data3D = ptr_new(fltarr(self.grid,self.grid,self.grid))
	foreach i, sps do begin
		*self.data3D += (*self.fxyz)[*,*,*,i]
	endforeach
end

pro draw_3D, fxyz, iso
	fmax = max(fxyz)
	isosurface, fxyz, fmax*iso, verts, conns
	L = (size(fxyz))[1] - 1
	c = L / 2
	shade=bytscl(sqrt((verts[0,*]-c)^2+(verts[1,*]-c)^2+(verts[2,*]-c)^2))
	Ll = L * .2
	Lr = L * .8
	scale3, xrange=[Ll,Lr],yrange=[Ll,Lr],zrange=[Ll,Lr]
	nframes = 20
	!p.font = 0
	dev = !d.name
	for i = 0, nframes do begin
		set_plot, 'z'
		device, decompose=0, set_resolution=[640,480]
		surface, dist(2), /nodata, ax=40, az=360.*i/nframes+5, $
			xrange=[Ll,Lr], yrange=[Ll,Lr], zrange=[Ll,Lr], $
			/save, charsize=2
		image = polyshade(verts,conns,/t3d,shade=shade)
		snapshot = tvrd()
		set_plot, dev
		tv, snapshot
		index = strtrim(string(i),2)
		if i lt 10 then index = '0' + index
;		write_png, 'pic' + index + '.png', tvrd(/true)
		wait, 1
	endfor
end


pro draw_pic

;	parser = obj_new('argparse','Draw distribution function at a given (r,t)')
;	parser.add_argument('--grid', default=101,
;		help='number of grid points (default = 101)')
;	parser.add_argument('--nsp', default=4,
;		help='number of species (default = 4)')
;	parser.add_argument('--cut',
;		help='make a 2D cut [e.g. x,49,51]')
;	parser.add_argument('--sp', default=0,
;		help='choose a species to plot for 3D')
;	parser.add_argument('--iso',
;		help='Set the iso value (in ratio of fmax) for 3D' \
;			+ '(default = 0.2)')
;	parser.add_argument('--add',
;		help='Combining species [e.g. 1,3]')
;	parser.add_argument('--save-png', action='store_true',
;		help='save plots in png')
;	args = parser.parse_args()


	fname = 'NASA/24.dat'
	nss = 4
	grid = 101
	PD = ParticleDistribution(fname, nss, grid)
	PD.print
	loadct, 39
	device, decompose=0

	ax = *(PD.get('axes'))

	
	PD.addR, [1,3]
	fR = PD.get('addR')
;	tv, (*fR[0])[*,*,0]
;	wait, 100

	PD.add3D, [1,3]
	fxyz = PD.get('add3D')
	draw_3D, *fxyz, 0.3
;	xvolume, bytscl(*fxyz)
	wait, 100

end
