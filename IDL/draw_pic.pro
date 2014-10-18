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

function tracer, fname

	Np = lonarr(1)
	Nts = lonarr(1)
	openr, id, fname, /get_lun
	readf, id, Np, Nts
	pt = fltarr(Np*6, Nts)
	readu, id, pt
	close, id

	return, pt
end

pro draw_pic

	nss = 4
	fname = 'fields-01750.dat'
	nx = 1000
	nz = 800
	emf = Field(fname, nss, nx, nz)
	emf.print
	loadct, 39
	device, decompose=0, retain=2
	tvlct, 255,255,255,255
	!p.background = 255
	pt = tracer('out.dat')

	cut = 200
	xwid = (nx-cut*2)/0.9
	ywid = (nz-cut*2)/0.9
	window,0,xs=xwid,ys=ywid
	Ex = *(emf.get('Ez'))
	bg = bytscl(Ex(cut:nx-cut-1,cut:nz-cut-1))
; works for > 8.3
;	ct = colortable(39)
;	im = image(bg,margin=[0.05,0.05,0.1,0.05],rgb_table=39)
;	cb = colorbar(target=im,orientation=1,position=[0.91,0.05,0.96,0.95])

	xmin = (*(emf.get('xe')))[0]
	xmax = (*(emf.get('xe')))[-1]
	zmin = (*(emf.get('ze')))[0]
	zmax = (*(emf.get('ze')))[-1]
	xl = xmin+(xmax-xmin)*cut/nx
	xr = xmax-(xmax-xmin)*cut/nx
	zl = zmin+(zmax-zmin)*cut/nz
	zr = zmax-(zmax-zmin)*cut/nz
	for i = 10000, 0, -20 do begin
		tv, bg, (xwid-nx)/2+cut, (ywid-nz)/2+cut
;		im.refresh
		a = reform(pt[*,i],6,1000)
;		plt = plot(a(0,*),a(2,*),xrange=[xl,xr],yrange=[zl,zr], $
;			position=[0.05,0.05,0.9,0.95],/overplot, $
;			linestyle=6, symbol='o')
;		plt = scatterplot(a(0,*),a(2,*),xrange=[xl,xr],yrange=[zl,zr], $
;			position=[0.05,0.05,0.9,0.95],/overplot, $
;			symbol='o')
		plot,xrange=[xl,xr],yrange=[zl,zr],a(0,*),a(2,*), $
			psym=4,color=0,/noerase, $
			/xstyle,/ystyle,xmargin=[0,0],ymargin=[0,0], $
			position=[0.05,0.05,0.95,0.95]
		wait, 0.1
	endfor
	wait, 100

;	fname = 'NASA/24.dat'
;	grid = 101
;	PD = ParticleDistribution(fname, nss, grid)
;	PD.print
;	ax = *(PD.get('axes'))

	
;	PD.addR, [1,3]
;	fR = PD.get('addR')
;	tv, (*fR[0])[*,*,0]
;	wait, 100

;	PD.add3D, [1,3]
;	fxyz = PD.get('add3D')
;	draw_3D, *fxyz, 0.3
;	xvolume, bytscl(*fxyz)
;	wait, 100

end
