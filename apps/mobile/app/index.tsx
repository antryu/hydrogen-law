import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function HomePage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      // TODO: API 호출
      console.log('검색:', query);
      await new Promise(resolve => setTimeout(resolve, 1000));
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* 검색 영역 */}
        <View style={styles.searchCard}>
          <Text style={styles.searchTitle}>법령 검색</Text>

          <TextInput
            style={styles.searchInput}
            value={query}
            onChangeText={setQuery}
            placeholder="예: 수소충전소 설치 기준"
            placeholderTextColor="#9ca3af"
          />

          <TouchableOpacity
            style={[
              styles.searchButton,
              (!query || loading) && styles.searchButtonDisabled,
            ]}
            onPress={handleSearch}
            disabled={!query || loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.searchButtonText}>검색</Text>
            )}
          </TouchableOpacity>

          <View style={styles.badges}>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>LLM 미사용</Text>
            </View>
            <Text style={styles.badgeSeparator}>•</Text>
            <Text style={styles.badgeLabel}>1초 이내 응답</Text>
            <Text style={styles.badgeSeparator}>•</Text>
            <Text style={styles.badgeLabel}>100% 정확도</Text>
          </View>
        </View>

        {/* 통계 카드 */}
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>2</Text>
            <Text style={styles.statLabel}>수집된 법령</Text>
            <Text style={styles.statSubLabel}>고압가스법 + 수소법</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statNumber}>0</Text>
            <Text style={styles.statLabel}>저장된 조문</Text>
            <Text style={styles.statSubLabel}>초기 수집 대기 중</Text>
          </View>
        </View>

        <View style={styles.statCardFull}>
          <Text style={styles.statNumber}>&lt;1초</Text>
          <Text style={styles.statLabel}>평균 응답 시간</Text>
          <Text style={styles.statSubLabel}>LLM 대비 10배 빠름</Text>
        </View>

        {/* 기능 소개 */}
        <View style={styles.featureCard}>
          <Text style={styles.featureTitle}>하이브리드 검색</Text>
          <Text style={styles.featureDescription}>
            벡터 검색(70%) + BM25(30%)로 의미와 키워드를 모두 고려
          </Text>
          <Text style={styles.featureItem}>• 한국어 특화 임베딩 모델</Text>
          <Text style={styles.featureItem}>• 규칙 기반 재랭킹</Text>
          <Text style={styles.featureItem}>• 조항 간 참조 자동 추출</Text>
        </View>

        <View style={styles.featureCard}>
          <Text style={styles.featureTitle}>컴플라이언스 체크</Text>
          <Text style={styles.featureDescription}>
            사업 유형별 필수 법령 자동 매칭 (LLM 없음)
          </Text>
          <Text style={styles.featureItem}>• 수소충전소 설치/운영</Text>
          <Text style={styles.featureItem}>• 수소 생산 시설</Text>
          <Text style={styles.featureItem}>• 수소 저장소</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  scrollContent: {
    padding: 16,
  },
  searchCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  searchTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 16,
  },
  searchInput: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 12,
  },
  searchButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    padding: 14,
    alignItems: 'center',
  },
  searchButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  searchButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  badges: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
  },
  badge: {
    backgroundColor: '#d1fae5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  badgeText: {
    color: '#047857',
    fontSize: 12,
  },
  badgeSeparator: {
    color: '#6b7280',
    fontSize: 12,
    marginHorizontal: 8,
  },
  badgeLabel: {
    color: '#6b7280',
    fontSize: 12,
  },
  statsContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  statCardFull: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  statNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#3b82f6',
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 14,
    color: '#4b5563',
  },
  statSubLabel: {
    fontSize: 12,
    color: '#9ca3af',
    marginTop: 4,
  },
  featureCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8,
  },
  featureDescription: {
    fontSize: 14,
    color: '#4b5563',
    marginBottom: 12,
  },
  featureItem: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 4,
  },
});
