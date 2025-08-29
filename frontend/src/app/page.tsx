'use client';

import React, { useState, useEffect } from 'react';
import { vulnerabilityApi } from '@/api/client';
import type { Vulnerability, VulnerabilityListResponse } from '@/types/vulnerability';
import VulnerabilityCard from '@/components/vulnerability/VulnerabilityCard';
import SearchAndFilters from '@/components/vulnerability/SearchAndFilters';
import Pagination from '@/components/ui/Pagination';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { formatNumber } from '@/lib/utils';
import { Shield, AlertTriangle, Building2, Package, Loader2 } from 'lucide-react';

interface SearchFilters {
  query: string;
  vendor: string;
  product: string;
  ransomware_only: boolean;
  date_from: string;
  date_to: string;
}

export default function Home() {
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchFilters, setSearchFilters] = useState<SearchFilters | null>(null);
  
  const PER_PAGE = 12;

  const fetchVulnerabilities = async (page: number = 1, filters?: SearchFilters) => {
    try {
      setLoading(true);
      
      let response: VulnerabilityListResponse;
      
      if (filters && (filters.query || filters.vendor || filters.product || filters.ransomware_only || filters.date_from || filters.date_to)) {
        // 검색 API 사용
        response = await vulnerabilityApi.searchVulnerabilities({
          ...filters,
          page,
          per_page: PER_PAGE
        });
      } else {
        // 기본 목록 API 사용
        response = await vulnerabilityApi.getVulnerabilities({
          page,
          per_page: PER_PAGE,
          sort_by: 'date_added',
          sort_order: 'desc'
        });
      }

      setVulnerabilities(response.items);
      setTotalCount(response.total);
      setTotalPages(response.pages);
      setCurrentPage(response.page);
    } catch (error) {
      console.error('Failed to fetch vulnerabilities:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVulnerabilities(1);
  }, []);

  const handleSearch = (filters: SearchFilters) => {
    setSearchFilters(filters);
    setCurrentPage(1);
    fetchVulnerabilities(1, filters);
  };

  const handleReset = () => {
    setSearchFilters(null);
    setCurrentPage(1);
    fetchVulnerabilities(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    fetchVulnerabilities(page, searchFilters || undefined);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">
              CISA KEV 모니터링 시스템
            </h1>
          </div>
          <p className="text-gray-600">
            CISA Known Exploited Vulnerabilities 데이터를 실시간으로 모니터링합니다.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Shield className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">전체 취약점</p>
                  <p className="text-2xl font-bold">{formatNumber(totalCount)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-red-100 rounded-lg">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">랜섬웨어 관련</p>
                  <p className="text-2xl font-bold">
                    {formatNumber(vulnerabilities.filter(v => v.known_ransomware_use).length)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Building2 className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">현재 페이지</p>
                  <p className="text-2xl font-bold">{currentPage}/{totalPages}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Package className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">표시 중</p>
                  <p className="text-2xl font-bold">
                    {vulnerabilities.length}개
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filters */}
        <div className="mb-8">
          <SearchAndFilters
            onSearch={handleSearch}
            onReset={handleReset}
            loading={loading}
          />
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-2 text-gray-600">로딩 중...</span>
          </div>
        )}

        {/* Vulnerability List */}
        {!loading && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
              {vulnerabilities.map((vulnerability) => (
                <VulnerabilityCard
                  key={vulnerability.id}
                  vulnerability={vulnerability}
                />
              ))}
            </div>

            {vulnerabilities.length === 0 && (
              <div className="text-center py-12">
                <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-600 mb-2">
                  검색 결과가 없습니다
                </h3>
                <p className="text-gray-500">
                  다른 검색어나 필터를 사용해 보세요.
                </p>
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center">
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
