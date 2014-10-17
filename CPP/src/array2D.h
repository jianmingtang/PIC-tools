#ifdef ARRAY2D_DEBUG
#include <iostream>
#endif
#include <cstdio>


#ifndef ARRAY2D_H
#define ARRAY2D_H


/**
 *  This is a simple class for a 2D array.
 *  Default Copy and Assignment are done by reference.
 */
template <class T>
class Array2D {
private:
	// pointer to data storage
	T* data;
	// 1D pointer array for the first index
	T** p;
	// reference count
	// This has to be a pointer so that we can change the value,
	// 	but the object itself stays const.
	size_t *ref;
	// array dimensions
	size_t m_, n_, len;

	void Clear();
public:

	Array2D();
	Array2D(size_t, size_t);
	Array2D(size_t, size_t, T*);
	Array2D(const Array2D<T>&);
	inline T* operator[](size_t);
	inline const T* operator[](size_t) const;
	inline Array2D<T>& operator=(const Array2D<T>&);
	inline Array2D<T>& Copy() const;
	~Array2D();

	size_t Get_ref() const;
};

/**
 *  Empty constructor.
 */
template <class T>
Array2D<T>::Array2D() : data(NULL), p(NULL), ref(NULL) {}

/**
 *  Constructor without initialization.
 */
template <class T>
Array2D<T>::Array2D(size_t m, size_t n) : m_(m), n_(n) {
	size_t i;

	len = m * n;
	data = new T [len];
	p = new T* [m];
	p[0] = data;
	for (i=1; i<m; ++i)
		p[i] = p[i-1] + n;

	ref = new size_t;
	*ref = 1;
}

/**
 *  Constructor with initialization.
 */
template <class T>
Array2D<T>::Array2D(size_t m, size_t n, T* a) : m_(m), n_(n) {
	size_t i;

	len = m * n;
	data = new T [len];
	p = new T* [m];
	p[0] = data;
	for (i=1; i<m; ++i)
		p[i] = p[i-1] + n;
	for (i=0; i<len; ++i)
		data[i] = a[i];

	ref = new size_t;
	*ref = 1;
}

/**
 *  Copy constructor (by reference).
 */
template <class T>
Array2D<T>::Array2D(const Array2D<T>& A) : m_(A.m_), n_(A.n_),
		len(A.len), data(A.data), p(A.p), ref(A.ref) {
// copy by value
/*
	size_t i;

	data = new T [len];
	p = new T* [m_];
	p[0] = data;
	for (i=1; i<m_; ++i)
		p[i] = p[i-1] + n_;
	for (i=0; i<len; ++i)
		data[i] = A[0][i];
*/
#ifdef ARRAY2D_DEBUG
	std::cerr << "Copy: " << A[0] << "->" << data << std::endl;
#endif
	if (A.ref != NULL) (*(A.ref))++;
}

/**
 *  First index; Set item.
 */
template <class T>
inline T* Array2D<T>::operator[](size_t i) {
	return p[i];
}

/**
 *  First index; Get item.
 */
template <class T>
inline const T* Array2D<T>::operator[](size_t i) const {
	return p[i];
}

/**
 *  Assign by reference.
 *	Input by & reduces one copy-constructor call.
 *	Return by & reduces one copy-constructor call.
 */
template <class T>
inline Array2D<T>& Array2D<T>::operator=(const Array2D<T>& A) {
	size_t i;

	m_ = A.m_; n_ = A.n_; len = A.len;

// assign by value
/*
	data = new T [len];
	p = new T* [m_];
	p[0] = data;
	for (i=1; i<m_; ++i)
		p[i] = p[i-1] + n_;
	for (i=0; i<len; ++i)
		data[i] = A[0][i];
*/

// assign by reference
	if (ref != NULL) {
		(*ref)--;
		if (*ref == 0) Clear();
	}
	data = A.data;
	p = A.p;
	ref = A.ref;
	if (A.ref != NULL) (*(A.ref))++;

#ifdef ARRAY2D_DEBUG
	std::cerr << "Assign: " << A[0] << "->" << data << std::endl;
#endif

	return *this;
}

/**
 *  Create a copy (by value).
 */
template <class T>
inline Array2D<T>& Array2D<T>::Copy() const {
	size_t i;
	Array2D<T> C(m_,n_,data);
	return C;
}

/**
 *  Clear the memory area. Call only when the reference count is zero.
 */
template <class T>
void Array2D<T>::Clear() {
	if (data != NULL) delete [] data;
	if (p != NULL) delete [] p;
	delete ref;
#ifdef ARRAY2D_DEBUG
	std::cerr << "Delete: " << data << std::endl;
#endif
}

/**
 *  Destructor
 */
template <class T>
Array2D<T>::~Array2D() {
	if (ref != NULL) {
		(*ref)--;
		if (*ref == 0) Clear();
	}
#ifdef ARRAY2D_DEBUG
	std::cerr << "Destroy: " << data << " ";
	std::cerr << "Ref count: " << " " << *ref << std::endl;
#endif
}

/**
 *  Get the reference count
 */
template <class T>
size_t Array2D<T>::Get_ref() const {
	return *(this->ref);
}


#endif /* ARRAY2D_H */
