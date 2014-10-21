;
;    draw_pic.pro:
;       Draw particle in cell data in 2D and 3D formats.
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


@ParticleDistribution
@Field

pro draw_3D, fxyz, iso, ax
	grid = (size(fxyz))[1]
	scale = (ax[-1] - ax[0]) / grid
	fmax = max(fxyz)
	isosurface, fxyz, fmax*iso, verts, conns
	verts = (verts - grid/2) * scale
	shade=bytscl(sqrt((verts[0,*])^2+(verts[1,*])^2+(verts[2,*])^2))
	Ll = ax[0] / 2
	Lr = ax[-1] /2
	scale3, xrange=[Ll,Lr],yrange=[Ll,Lr],zrange=[Ll,Lr]
	nframes = 20
	!p.font = 0
	dev = !d.name
	device, decompose=0
	window,0,xs=800,ys=600
	loadct, 39
	for i = 0, nframes do begin
		set_plot, 'z'
		device, decompose=0, set_resolution=[800,600]
		surface, dist(2), /nodata, ax=40, az=360.*i/nframes+5, $
			xrange=[Ll,Lr], yrange=[Ll,Lr], zrange=[Ll,Lr], $
			/xstyle, /ystyle, /zstyle, $
			/save, charsize=2, title='fxyz', $
			xtitle='Vx', ytitle='Vy', ztitle='Vz'
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

pro draw_dist_2D, data, title, range
	scale = (range[1] - range[0]) / (size(data))[1]
	im = image(data, title=title, font_size=20, $
		rgb_table=13, min_value=min(data), max_value=max(data), $
		margin=[0.12,0.12,0.2,0.1], aspect_ratio=0)
	xax = axis('x', title='Vx', location=[0.12,0.12], $
		axis_range=range, coord_transform=[range[0],scale], $
		color='yellow', text_color='black', tickfont_size=16)
	yax = axis('y', title='Vy', location=[0.12,0.12], $
		axis_range=range, coord_transform=[range[0],scale], $
		color='yellow', text_color='black', tickfont_size=16)
	cb = colorbar(target=im, orientation=1, font_size=16, $
		position=[0.9,0.12,0.96,0.9], /border)
end


pro draw_pic, fname=fname

;
; Define number of species and grids
	nss = 4
	grid = 101

;
; Read in distribution function
	PD = ParticleDistribution(fname, nss, grid)
;
; Print out location	
	PD.print
;
; Get axes
	ax = PD.get('axes')
	xl = ax[0,1]
	xr = ax[-1,1]
;
; Get fxy, species 3
	fxy = (PD.get('fxy'))[*,*,3]
;
; Make a 2D plot
	draw_dist_2D, fxy, 'fxy,s3', [xl,xr]


;
; Add species 1 & 3 of the reduced f's
	PD.addR, [1,3]
;
; Get reduced f (0:xy, 1:xz, 2:yz)
; In this case, fRxy is a pointer
	fRxy = (PD.get('addR'))[0]
;
; Make a 2D plot
	draw_dist_2D, *fRxy, 'fxy', [xl,xr]

;
; Make a slice of 3D data 
	PD.cut, 'z', 0, 100
;
; Add species 1 & 3 of the slice
	PD.add2D, [1,3]
;
; Get the slice
	fcut = PD.get('add2D')
;
; Make a 2D plot
	draw_dist_2D, fcut, 'fcut,z,30,70', [xl,xr]

;
; Add species 1 & 3 of fxyz
	PD.add3D, [1,3]
	fxyz = PD.get('add3D')
;
; Make a 3D plot
	draw_3D, fxyz, 0.3, ax[*,1]
	wait, 100

;
; IDL's interative tool for 3D data
;	xvolume, bytscl(*fxyz)
end
