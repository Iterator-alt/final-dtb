"""
Enhanced Brand Detection Utility - Stage 2

This module provides sophisticated brand detection capabilities with advanced
ranking detection, context analysis, and multi-pattern matching for Stage 2.
"""

import re
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from src.workflow.state import BrandDetectionResult
from src.config.settings import get_settings

@dataclass
class MatchContext:
    """Context information around a brand match."""
    text: str
    start_pos: int
    end_pos: int
    surrounding_context: str
    sentence: str
    paragraph: str

@dataclass
class RankingMatch:
    """Information about a detected ranking."""
    position: int
    confidence: float
    context: str
    pattern_type: str  # "ordinal", "numeric", "keyword", "list"
    proximity_to_brand: int  # Distance from brand mention

class EnhancedBrandDetector:
    """Advanced brand detection with sophisticated ranking detection for Stage 2."""
    
    def __init__(self, config=None):
        """Initialize the enhanced brand detector with configuration."""
        self.config = config or get_settings().brand
        self.ranking_keywords = get_settings().ranking_keywords
        
        # Prepare brand variations for efficient matching
        self.brand_patterns = self._prepare_brand_patterns()
        self.ranking_patterns = self._prepare_advanced_ranking_patterns()
        
        # Advanced ranking detection patterns
        self.ordinal_patterns = self._prepare_ordinal_patterns()
        self.list_patterns = self._prepare_list_patterns()
        self.keyword_ranking_patterns = self._prepare_keyword_ranking_patterns()
    
    def _prepare_brand_patterns(self) -> List[re.Pattern]:
        """Prepare regex patterns for brand matching."""
        patterns = []
        
        for variation in self.config.brand_variations:
            # Escape special regex characters
            escaped = re.escape(variation)
            
            if self.config.partial_match:
                # Allow partial matches within word boundaries
                pattern = rf'\b{escaped}\b'
            else:
                # Exact match only
                pattern = rf'^{escaped}$'
            
            flags = 0 if self.config.case_sensitive else re.IGNORECASE
            patterns.append(re.compile(pattern, flags))
        
        return patterns
    
    def _prepare_advanced_ranking_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Prepare comprehensive regex patterns for ranking detection."""
        patterns = {
            'ordinal': [],
            'numeric': [],
            'keyword': [],
            'list': []
        }
        
        # Ordinal patterns (1st, 2nd, 3rd, etc.)
        ordinal_pattern = r'\b(\d+)(?:st|nd|rd|th)\b'
        patterns['ordinal'].append(re.compile(ordinal_pattern, re.IGNORECASE))
        
        # Numeric patterns (#1, No. 1, etc.)
        numeric_patterns = [
            r'#(\d+)',
            r'no\.?\s*(\d+)',
            r'number\s+(\d+)',
            r'rank\s*[:#]?\s*(\d+)',
            r'position\s*[:#]?\s*(\d+)'
        ]
        for pattern in numeric_patterns:
            patterns['numeric'].append(re.compile(pattern, re.IGNORECASE))
        
        # Keyword-based ranking patterns
        keyword_patterns = [
            r'\b(top|best|leading|premier|foremost|primary)\b',
            r'\b(number\s+one|no\.\s*1|#1)\b',
            r'\b(first|1st)\s+(choice|pick|option)\b',
            r'\b(industry\s+leader|market\s+leader)\b'
        ]
        for pattern in keyword_patterns:
            patterns['keyword'].append(re.compile(pattern, re.IGNORECASE))
        
        # List-based patterns
        list_patterns = [
            r'(\d+)\.\s+',  # Numbered lists
            r'^\s*(\d+)\)\s+',  # Parenthetical numbering
            r'^\s*•\s*(\d+)',  # Bulleted numbering
        ]
        for pattern in list_patterns:
            patterns['list'].append(re.compile(pattern, re.MULTILINE))
        
        return patterns
    
    def _prepare_ordinal_patterns(self) -> List[re.Pattern]:
        """Prepare specific ordinal number patterns."""
        patterns = []
        
        # Standard ordinals (1st through 100th)
        for i in range(1, 101):
            if i == 1:
                suffix = "st"
            elif i == 2:
                suffix = "nd"
            elif i == 3:
                suffix = "rd"
            else:
                suffix = "th"
            
            pattern = rf'\b{i}{suffix}\b'
            patterns.append(re.compile(pattern, re.IGNORECASE))
        
        return patterns
    
    def _prepare_list_patterns(self) -> List[re.Pattern]:
        """Prepare patterns for detecting items in ranked lists."""
        patterns = []
        
        list_indicators = [
            r'^\s*(\d+)\.\s+',  # 1. Item
            r'^\s*(\d+)\)\s+',  # 1) Item
            r'^\s*\((\d+)\)\s+',  # (1) Item
            r'^\s*-\s*(\d+)\.\s+',  # - 1. Item
            r'^\s*•\s*(\d+)\.\s+',  # • 1. Item
        ]
        
        for pattern in list_indicators:
            patterns.append(re.compile(pattern, re.MULTILINE))
        
        return patterns
    
    def _prepare_keyword_ranking_patterns(self) -> Dict[str, int]:
        """Prepare keyword-to-position mappings."""
        return {
            'first': 1,
            '1st': 1,
            'top': 1,
            'best': 1,
            'leading': 1,
            'premier': 1,
            'foremost': 1,
            'primary': 1,
            'number one': 1,
            'no. 1': 1,
            '#1': 1,
            'second': 2,
            '2nd': 2,
            'third': 3,
            '3rd': 3,
            'fourth': 4,
            '4th': 4,
            'fifth': 5,
            '5th': 5
        }
    
    def detect_brand(self, text: str, include_ranking: bool = True) -> BrandDetectionResult:
        """
        Detect brand mentions in the given text with enhanced ranking detection.
        
        Args:
            text: Text to analyze
            include_ranking: Whether to detect ranking information (Stage 2)
            
        Returns:
            BrandDetectionResult with detection information
        """
        if not text:
            return BrandDetectionResult(found=False, confidence=0.0)
        
        matches = self._find_brand_matches(text)
        
        if not matches:
            return BrandDetectionResult(found=False, confidence=0.0)
        
        # Calculate confidence based on number and quality of matches
        confidence = self._calculate_confidence(matches, text)
        
        # Extract match information
        match_texts = [match.text for match in matches]
        best_context = max(matches, key=lambda m: len(m.surrounding_context)).surrounding_context
        
        result = BrandDetectionResult(
            found=True,
            confidence=confidence,
            matches=match_texts,
            context=best_context
        )
        
        # Enhanced ranking detection for Stage 2
        if include_ranking:
            # Temporarily disabled to focus on core brand detection
            # ranking_info = self._detect_advanced_ranking(text, matches)
            # result.ranking_position = ranking_info.get('position')
            # result.ranking_context = ranking_info.get('context')
            pass
        
        return result
    
    def _find_brand_matches(self, text: str) -> List[MatchContext]:
        """Find all brand matches in the text with enhanced context."""
        matches = []
        
        for pattern in self.brand_patterns:
            for match in pattern.finditer(text):
                context = self._extract_enhanced_context(text, match)
                matches.append(context)
        
        return matches
    
    def _extract_enhanced_context(self, text: str, match: re.Match) -> MatchContext:
        """Extract enhanced context around a brand match."""
        start, end = match.span()
        
        # Get surrounding context (100 characters before and after for better analysis)
        context_start = max(0, start - 100)
        context_end = min(len(text), end + 100)
        surrounding_context = text[context_start:context_end]
        
        # Find the sentence containing the match
        sentence = self._find_containing_sentence(text, start, end)
        
        # Find the paragraph containing the match
        paragraph = self._find_containing_paragraph(text, start, end)
        
        return MatchContext(
            text=match.group(),
            start_pos=start,
            end_pos=end,
            surrounding_context=surrounding_context,
            sentence=sentence,
            paragraph=paragraph
        )
    
    def _find_containing_sentence(self, text: str, start: int, end: int) -> str:
        """Find the sentence that contains the match."""
        sentence_endings = ['.', '!', '?', '\n', ';']
        
        # Find sentence start
        sentence_start = 0
        for i in range(start - 1, -1, -1):
            if text[i] in sentence_endings:
                sentence_start = i + 1
                break
        
        # Find sentence end
        sentence_end = len(text)
        for i in range(end, len(text)):
            if text[i] in sentence_endings:
                sentence_end = i + 1
                break
        
        return text[sentence_start:sentence_end].strip()
    
    def _find_containing_paragraph(self, text: str, start: int, end: int) -> str:
        """Find the paragraph that contains the match."""
        # Find paragraph boundaries (double newlines or significant breaks)
        paragraph_breaks = ['\n\n', '\r\n\r\n']
        
        # Find paragraph start
        paragraph_start = 0
        for break_pattern in paragraph_breaks:
            last_break = text.rfind(break_pattern, 0, start)
            if last_break != -1:
                paragraph_start = max(paragraph_start, last_break + len(break_pattern))
        
        # Find paragraph end
        paragraph_end = len(text)
        for break_pattern in paragraph_breaks:
            next_break = text.find(break_pattern, end)
            if next_break != -1:
                paragraph_end = min(paragraph_end, next_break)
        
        return text[paragraph_start:paragraph_end].strip()
    
    def _calculate_confidence(self, matches: List[MatchContext], text: str) -> float:
        """Calculate enhanced confidence score based on matches and context."""
        if not matches:
            return 0.0
        
        base_confidence = 0.6  # Base confidence for any match
        
        # Bonus for multiple matches
        multiple_match_bonus = min(0.2, len(matches) * 0.05)
        
        # Bonus for exact brand name matches
        exact_match_bonus = 0.0
        for match in matches:
            if match.text.lower() == self.config.target_brand.lower():
                exact_match_bonus = 0.15
                break
        
        # Context quality bonus (enhanced)
        context_bonus = self._calculate_enhanced_context_bonus(matches)
        
        # Paragraph structure bonus
        structure_bonus = self._calculate_structure_bonus(matches, text)
        
        confidence = base_confidence + multiple_match_bonus + exact_match_bonus + context_bonus + structure_bonus
        return min(1.0, confidence)  # Cap at 1.0
    
    def _calculate_enhanced_context_bonus(self, matches: List[MatchContext]) -> float:
        """Calculate enhanced bonus based on context quality."""
        positive_keywords = [
            'best', 'top', 'leading', 'excellent', 'great', 'recommend', 'outstanding',
            'powerful', 'innovative', 'solution', 'platform', 'tool', 'premier',
            'industry leader', 'market leader', 'award-winning', 'recognized'
        ]
        
        negative_keywords = [
            'worst', 'bad', 'poor', 'avoid', 'terrible', 'disappointing', 'failed'
        ]
        
        ranking_indicators = [
            'rank', 'position', 'place', 'top', 'list', 'comparison', 'versus', 'vs'
        ]
        
        context_score = 0.0
        
        for match in matches:
            context_lower = match.surrounding_context.lower()
            
            # Positive context
            positive_count = sum(1 for keyword in positive_keywords if keyword in context_lower)
            context_score += positive_count * 0.02
            
            # Negative context (reduces confidence)
            negative_count = sum(1 for keyword in negative_keywords if keyword in context_lower)
            context_score -= negative_count * 0.05
            
            # Ranking context (increases confidence for Stage 2)
            ranking_count = sum(1 for keyword in ranking_indicators if keyword in context_lower)
            context_score += ranking_count * 0.03
        
        return max(-0.15, min(0.15, context_score))  # Cap between -0.15 and 0.15
    
    def _calculate_structure_bonus(self, matches: List[MatchContext], text: str) -> float:
        """Calculate bonus based on document structure (lists, headings, etc.)."""
        structure_score = 0.0
        
        for match in matches:
            # Check if match appears in a list structure
            if self._is_in_list_structure(match.sentence):
                structure_score += 0.05
            
            # Check if match appears near headings or titles
            if self._is_near_heading(match.paragraph):
                structure_score += 0.03
            
            # Check if match appears in a comparison context
            if self._is_in_comparison_context(match.surrounding_context):
                structure_score += 0.04
        
        return min(0.1, structure_score)  # Cap at 0.1
    
    def _is_in_list_structure(self, sentence: str) -> bool:
        """Check if the sentence appears to be part of a list."""
        list_indicators = [
            r'^\s*\d+\.',  # 1.
            r'^\s*\d+\)',  # 1)
            r'^\s*•',      # •
            r'^\s*-',      # -
            r'^\s*\*',     # *
        ]
        
        for pattern in list_indicators:
            if re.match(pattern, sentence.strip()):
                return True
        return False
    
    def _is_near_heading(self, paragraph: str) -> bool:
        """Check if the paragraph contains heading-like structures."""
        heading_patterns = [
            r'^[A-Z][A-Za-z\s]+:',  # Title:
            r'^#+ ',                 # Markdown headers
            r'^\d+\.\s+[A-Z]',      # 1. Section
        ]
        
        for pattern in heading_patterns:
            if re.search(pattern, paragraph, re.MULTILINE):
                return True
        return False
    
    def _is_in_comparison_context(self, context: str) -> bool:
        """Check if the context suggests a comparison or ranking."""
        comparison_keywords = [
            'compared to', 'versus', 'vs', 'against', 'better than',
            'similar to', 'unlike', 'in contrast to', 'alternatives to'
        ]
        
        context_lower = context.lower()
        return any(keyword in context_lower for keyword in comparison_keywords)
    
    def _detect_advanced_ranking(self, text: str, brand_matches: List[MatchContext]) -> Dict[str, Optional[any]]:
        """
        Advanced ranking detection with multiple detection strategies.
        
        Returns:
            Dictionary with 'position' and 'context' keys
        """
        if not brand_matches:
            return {'position': None, 'context': None}
        
        ranking_candidates = []
        
        for brand_match in brand_matches:
            # Strategy 1: Ordinal detection in sentence
            ordinal_rankings = self._detect_ordinal_rankings(brand_match.sentence, brand_match)
            ranking_candidates.extend(ordinal_rankings)
            
            # Strategy 2: List position detection
            list_rankings = self._detect_list_position(text, brand_match)
            ranking_candidates.extend(list_rankings)
            
            # Strategy 3: Keyword-based ranking
            keyword_rankings = self._detect_keyword_rankings(brand_match.paragraph, brand_match)
            ranking_candidates.extend(keyword_rankings)
            
            # Strategy 4: Numeric pattern detection
            numeric_rankings = self._detect_numeric_patterns(brand_match.surrounding_context, brand_match)
            ranking_candidates.extend(numeric_rankings)
        
        # Select the best ranking candidate
        if ranking_candidates:
            best_ranking = max(ranking_candidates, key=lambda r: r.confidence)
            return {
                'position': best_ranking.position,
                'context': best_ranking.context
            }
        
        return {'position': None, 'context': None}
    
    def _detect_ordinal_rankings(self, sentence: str, brand_match: MatchContext) -> List[RankingMatch]:
        """Detect ordinal rankings (1st, 2nd, 3rd, etc.) in sentence."""
        rankings = []
        
        for pattern in self.ranking_patterns['ordinal']:
            for match in pattern.finditer(sentence):
                try:
                    # Extract the numeric part
                    position_str = match.group(1)
                    position = int(position_str)
                    
                    if 1 <= position <= 100:  # Reasonable ranking range
                        # Calculate proximity to brand mention
                        proximity = abs(match.start() - (brand_match.start_pos - sentence.find(brand_match.text)))
                        
                        # Higher confidence for closer proximity
                        confidence = max(0.6, 1.0 - (proximity / 100))
                        
                        rankings.append(RankingMatch(
                            position=position,
                            confidence=confidence,
                            context=sentence,
                            pattern_type="ordinal",
                            proximity_to_brand=proximity
                        ))
                        
                except (ValueError, IndexError):
                    continue
        
        return rankings
    
    def _detect_list_position(self, text: str, brand_match: MatchContext) -> List[RankingMatch]:
        """Detect position in numbered lists."""
        rankings = []
        
        # Find the paragraph containing the brand match
        paragraph_start = text.find(brand_match.paragraph)
        if paragraph_start == -1:
            return rankings
        
        # Look for list patterns before the brand match
        lines = brand_match.paragraph.split('\n')
        brand_line_index = -1
        
        # Find which line contains the brand
        for i, line in enumerate(lines):
            if brand_match.text in line:
                brand_line_index = i
                break
        
        if brand_line_index == -1:
            return rankings
        
        # Check if this line starts with a number
        brand_line = lines[brand_line_index].strip()
        for pattern in self.list_patterns:
            match = pattern.match(brand_line)
            if match:
                try:
                    position = int(match.group(1))
                    if 1 <= position <= 50:  # Reasonable list range
                        rankings.append(RankingMatch(
                            position=position,
                            confidence=0.8,  # High confidence for explicit list structure
                            context=brand_match.paragraph,
                            pattern_type="list",
                            proximity_to_brand=0
                        ))
                except (ValueError, IndexError):
                    continue
        
        return rankings
    
    def _detect_keyword_rankings(self, paragraph: str, brand_match: MatchContext) -> List[RankingMatch]:
        """Detect keyword-based rankings (top, best, leading, etc.)."""
        rankings = []
        
        for pattern in self.ranking_patterns['keyword']:
            for match in pattern.finditer(paragraph):
                keyword = match.group().lower()
                
                # Map keyword to position
                position = self.keyword_ranking_patterns.get(keyword)
                if position:
                    # Calculate proximity to brand mention
                    proximity = abs(match.start() - paragraph.find(brand_match.text))
                    
                    # Confidence based on keyword type and proximity
                    if keyword in ['top', 'best', 'leading']:
                        base_confidence = 0.7
                    elif keyword in ['#1', 'number one', 'first']:
                        base_confidence = 0.9
                    else:
                        base_confidence = 0.6
                    
                    confidence = max(0.4, base_confidence - (proximity / 200))
                    
                    rankings.append(RankingMatch(
                        position=position,
                        confidence=confidence,
                        context=paragraph,
                        pattern_type="keyword",
                        proximity_to_brand=proximity
                    ))
        
        return rankings
    
    def _detect_numeric_patterns(self, context: str, brand_match: MatchContext) -> List[RankingMatch]:
        """Detect numeric ranking patterns (#1, No. 1, etc.)."""
        rankings = []
        
        for pattern in self.ranking_patterns['numeric']:
            for match in pattern.finditer(context):
                try:
                    position_str = match.group(1)
                    position = int(position_str)
                    
                    if 1 <= position <= 100:  # Reasonable ranking range
                        # Calculate proximity to brand mention
                        proximity = abs(match.start() - context.find(brand_match.text))
                        
                        # Higher confidence for explicit numeric indicators
                        confidence = max(0.7, 1.0 - (proximity / 150))
                        
                        rankings.append(RankingMatch(
                            position=position,
                            confidence=confidence,
                            context=context,
                            pattern_type="numeric",
                            proximity_to_brand=proximity
                        ))
                        
                except (ValueError, IndexError):
                    continue
        
        return rankings
    
    def batch_detect(self, texts: List[str], include_ranking: bool = True) -> List[BrandDetectionResult]:
        """Batch process multiple texts for brand detection with ranking."""
        return [self.detect_brand(text, include_ranking) for text in texts]
    
    def get_detection_summary(self, results: List[BrandDetectionResult]) -> Dict[str, any]:
        """Generate an enhanced summary of detection results including ranking data."""
        total = len(results)
        found_count = sum(1 for r in results if r.found)
        ranked_count = sum(1 for r in results if r.found and r.ranking_position)
        
        if found_count == 0:
            avg_confidence = 0.0
            avg_ranking = None
        else:
            avg_confidence = sum(r.confidence for r in results if r.found) / found_count
            
            rankings = [r.ranking_position for r in results if r.found and r.ranking_position]
            avg_ranking = sum(rankings) / len(rankings) if rankings else None
        
        return {
            'total_analyzed': total,
            'brand_mentions_found': found_count,
            'ranked_mentions_found': ranked_count,
            'detection_rate': found_count / total if total > 0 else 0.0,
            'ranking_detection_rate': ranked_count / found_count if found_count > 0 else 0.0,
            'average_confidence': avg_confidence,
            'average_ranking_position': avg_ranking,
            'best_ranking': min([r.ranking_position for r in results if r.found and r.ranking_position], default=None),
            'unique_matches': list(set(match for r in results for match in r.matches))
        }

# Backward compatibility - replace the original class
BrandDetector = EnhancedBrandDetector

# Utility functions for easy usage
def detect_brand_in_text(text: str, config=None, include_ranking: bool = True) -> BrandDetectionResult:
    """Simple function to detect brand in a single text with ranking."""
    detector = EnhancedBrandDetector(config)
    return detector.detect_brand(text, include_ranking)

def detect_brand_batch(texts: List[str], config=None, include_ranking: bool = True) -> List[BrandDetectionResult]:
    """Simple function to detect brand in multiple texts with ranking."""
    detector = EnhancedBrandDetector(config)
    return detector.batch_detect(texts, include_ranking)