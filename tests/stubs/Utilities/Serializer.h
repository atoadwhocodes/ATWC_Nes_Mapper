#pragma once
#include "pch.h"
struct Serializer {
 bool saving; std::vector<uint8_t> data; size_t pos=0;
 bool IsSaving() const {return saving;}
 template<class T> void value(T& v) {
  if(saving) {auto p=reinterpret_cast<uint8_t*>(&v);data.insert(data.end(),p,p+sizeof(v));}
  else {assert(pos+sizeof(v)<=data.size());std::memcpy(&v,data.data()+pos,sizeof(v));pos+=sizeof(v);}
 }
};
#define SV(v) s.value(v)
#define SVArray(v,n) s.value(v)
