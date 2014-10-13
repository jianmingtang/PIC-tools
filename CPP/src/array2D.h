#include <iostream>

#ifndef ARRAY2D_H
#define ARRAY2D_H

/**
 *  This is a simple class for a 2D array
 *  Right now everything is by value
 */
template <class T>
class Array2D {
private:
	T* data;
	T** p;
public:
	unsigned int m,n,len;
	Array2D();
	Array2D(unsigned int, unsigned int);
	Array2D(unsigned int, unsigned int, T*);
	Array2D(const Array2D<T>&);
// write and read
	inline T* operator[](unsigned int);
	inline const T* operator[](unsigned int) const;
// return & reduces one extra copy constructor
	inline Array2D<T>& operator=(Array2D<T>);
	~Array2D();
};

template <class T>
Array2D<T>::Array2D() {
	data = NULL;
}

template <class T>
Array2D<T>::Array2D(unsigned int m, unsigned int n) : m(m), n(n) {
	unsigned int i;

	len = m * n;
	data = new T [len];
	p = new T* [m];
	p[0] = data;
	for (i=1; i<m; ++i)
		p[i] = p[i-1] + n;
}

template <class T>
Array2D<T>::Array2D(unsigned int m, unsigned int n, T* a) : m(m), n(n) {
	unsigned int i;

	len = m * n;
	data = new T [len];
	p = new T* [m];
	p[0] = data;
	for (i=1; i<m; ++i)
		p[i] = p[i-1] + n;
	for (i=0; i<len; ++i)
		data[i] = a[i];
}

// copy constructor
template <class T>
Array2D<T>::Array2D(const Array2D<T>& A) : m(A.m), n(A.n), len(A.len) {
	unsigned int i;

	data = new T [len];
	p = new T* [m];
	p[0] = data;
	for (i=1; i<m; ++i)
		p[i] = p[i-1] + n;
	for (i=0; i<len; ++i)
		data[i] = A[0][i];
//	std::cerr << "Copy: " << A[0] << "->" << data << std::endl;
}

template <class T>
inline T* Array2D<T>::operator[](unsigned int i) {
	return p[i];
}

template <class T>
inline const T* Array2D<T>::operator[](unsigned int i) const {
	return p[i];
}

template <class T>
inline Array2D<T>& Array2D<T>::operator=(Array2D<T> A) {
	unsigned int i;

	m = A.m; n = A.n; len = A.len;
	data = new T [len];
	p = new T* [m];
	p[0] = data;
	for (i=1; i<m; ++i)
		p[i] = p[i-1] + n;
	for (i=0; i<len; ++i)
		data[i] = A[0][i];
//	std::cerr << "Assign: " << A[0] << "->" << data << std::endl;
	return *this;
}

template <class T>
Array2D<T>::~Array2D() {
//	std::cerr << "Ref count: " << data << " " << ref << std::endl;
	if (data != NULL) {
//		std::cerr << "Delete: " << data << std::endl;
		delete [] data;
		delete [] p;
	}
}

#endif /* ARRAY2D_H */
