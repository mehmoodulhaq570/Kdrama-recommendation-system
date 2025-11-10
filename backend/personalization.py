"""
Personalization Engine
Phase 2: Personalized Weighting

This module applies user-specific boosting to recommendation scores
based on learned preferences from user profiles.
"""

from typing import Dict, List, Optional
import math


class PersonalizationEngine:
    """
    Applies personalized weighting to recommendation results.

    Features:
    - Genre boosting based on user preferences
    - Actor boosting based on user preferences
    - Director boosting based on user preferences
    - Theme matching and boosting
    - User-specific alpha adjustment
    """

    def __init__(self):
        # Boosting factors (how much to multiply scores)
        self.genre_boost_factor = 0.5  # Up to 50% boost for favorite genres
        self.actor_boost_factor = 0.3  # Up to 30% boost for favorite actors
        self.director_boost_factor = 0.2  # Up to 20% boost for favorite directors
        self.theme_boost_factor = 0.4  # Up to 40% boost for matching themes

    def personalize_results(
        self, results: List[Dict], user_profile: Dict, apply_boosting: bool = True
    ) -> List[Dict]:
        """
        Apply personalization to recommendation results.

        Args:
            results: List of drama recommendations with scores
            user_profile: User preference profile
            apply_boosting: Whether to apply preference boosting

        Returns:
            Re-ranked and personalized results with explanation
        """
        if not user_profile or not apply_boosting:
            return results

        preferences = user_profile.get("preferences", {})

        # Apply boosting to each result
        for drama in results:
            base_score = drama.get("score", 0.5)

            # Calculate boost from various factors
            genre_boost = self._calculate_genre_boost(drama, preferences)
            actor_boost = self._calculate_actor_boost(drama, preferences)
            director_boost = self._calculate_director_boost(drama, preferences)
            theme_boost = self._calculate_theme_boost(drama, preferences)

            # Total boost multiplier (1.0 = no boost, 2.0 = double score)
            total_boost = 1.0 + genre_boost + actor_boost + director_boost + theme_boost

            # Apply boost to score
            personalized_score = base_score * total_boost

            # Store both scores and boost details
            drama["base_score"] = base_score
            drama["personalized_score"] = personalized_score
            drama["boost_multiplier"] = total_boost
            drama["boost_details"] = {
                "genre": genre_boost,
                "actor": actor_boost,
                "director": director_boost,
                "theme": theme_boost,
            }

        # Re-rank by personalized score
        results.sort(key=lambda x: x.get("personalized_score", 0), reverse=True)

        return results

    def _calculate_genre_boost(self, drama: Dict, preferences: Dict) -> float:
        """
        Calculate boost based on genre preferences.
        Returns boost value (0.0 to genre_boost_factor)
        """
        genre_prefs = preferences.get("genres", {})
        if not genre_prefs:
            return 0.0

        # Get drama genres
        genres_str = drama.get("Genre", drama.get("genres", ""))
        if not genres_str:
            return 0.0

        # Parse genres
        if isinstance(genres_str, str):
            genres = [g.strip() for g in genres_str.split(",")]
        else:
            genres = genres_str

        # Calculate average preference score for drama's genres
        matching_scores = []
        for genre in genres:
            if genre in genre_prefs:
                matching_scores.append(genre_prefs[genre])

        if not matching_scores:
            return 0.0

        # Use max preference (boost for best matching genre)
        max_pref = max(matching_scores)

        # Scale by boost factor
        return max_pref * self.genre_boost_factor

    def _calculate_actor_boost(self, drama: Dict, preferences: Dict) -> float:
        """
        Calculate boost based on actor preferences.
        Returns boost value (0.0 to actor_boost_factor)
        """
        actor_prefs = preferences.get("actors", {})
        if not actor_prefs:
            return 0.0

        # Get drama cast
        cast_str = drama.get("Cast", drama.get("cast", ""))
        if not cast_str:
            return 0.0

        # Parse cast
        if isinstance(cast_str, str):
            actors = [a.strip() for a in cast_str.split(",")]
        else:
            actors = cast_str

        # Calculate average preference score for drama's actors
        matching_scores = []
        for actor in actors:
            if actor in actor_prefs:
                matching_scores.append(actor_prefs[actor])

        if not matching_scores:
            return 0.0

        # Use max preference (boost for favorite actor)
        max_pref = max(matching_scores)

        # Scale by boost factor
        return max_pref * self.actor_boost_factor

    def _calculate_director_boost(self, drama: Dict, preferences: Dict) -> float:
        """
        Calculate boost based on director preferences.
        Returns boost value (0.0 to director_boost_factor)
        """
        director_prefs = preferences.get("directors", {})
        if not director_prefs:
            return 0.0

        # Get drama director
        director = drama.get("Director", drama.get("director", ""))
        if not director:
            return 0.0

        # Check if user has preference for this director
        if director not in director_prefs:
            return 0.0

        pref_score = director_prefs[director]

        # Scale by boost factor
        return pref_score * self.director_boost_factor

    def _calculate_theme_boost(self, drama: Dict, preferences: Dict) -> float:
        """
        Calculate boost based on theme preferences.
        Returns boost value (0.0 to theme_boost_factor)
        """
        theme_prefs = preferences.get("themes", {})
        if not theme_prefs:
            return 0.0

        # Get drama keywords/description
        keywords_str = drama.get("keywords", "")
        description = drama.get("Description", drama.get("description", ""))

        # Extract themes from drama
        drama_themes = set()

        # From keywords
        if keywords_str:
            if isinstance(keywords_str, str):
                drama_themes.update(
                    [k.strip().lower() for k in keywords_str.split(",")]
                )
            else:
                drama_themes.update([k.lower() for k in keywords_str])

        # From description (simple matching)
        if description:
            desc_lower = description.lower()
            for theme in theme_prefs.keys():
                if theme in desc_lower:
                    drama_themes.add(theme)

        if not drama_themes:
            return 0.0

        # Calculate average preference for matching themes
        matching_scores = []
        for theme in drama_themes:
            if theme in theme_prefs:
                matching_scores.append(theme_prefs[theme])

        if not matching_scores:
            return 0.0

        # Use average of matching themes
        avg_pref = sum(matching_scores) / len(matching_scores)

        # Scale by boost factor
        return avg_pref * self.theme_boost_factor

    def calculate_user_specific_alpha(
        self, user_profile: Dict, base_alpha: float
    ) -> float:
        """
        Calculate user-specific alpha (semantic vs lexical weight).

        Users with diverse interests → Higher semantic (explore)
        Users with focused interests → Higher lexical (exploit)

        Args:
            user_profile: User preference profile
            base_alpha: Base alpha from query analysis

        Returns:
            Adjusted alpha value (0.0 to 1.0)
        """
        if not user_profile:
            return base_alpha

        preferences = user_profile.get("preferences", {})
        genre_prefs = preferences.get("genres", {})

        if not genre_prefs:
            return base_alpha

        # Calculate diversity score (0 = focused, 1 = diverse)
        diversity = self._calculate_preference_diversity(genre_prefs)

        # Adjust alpha based on diversity
        # Diverse users: increase semantic weight (explore)
        # Focused users: increase lexical weight (exploit)

        if diversity > 0.7:  # Very diverse tastes
            # Increase semantic weight (higher alpha)
            return min(base_alpha + 0.15, 0.95)
        elif diversity < 0.3:  # Very focused tastes
            # Increase lexical weight (lower alpha)
            return max(base_alpha - 0.1, 0.3)
        else:
            # Moderate diversity, use base alpha
            return base_alpha

    def _calculate_preference_diversity(self, preferences: Dict) -> float:
        """
        Calculate how diverse user's preferences are.

        Returns:
            Diversity score (0.0 = all preference on one item, 1.0 = evenly distributed)
        """
        if not preferences:
            return 0.5  # Neutral

        values = list(preferences.values())
        if len(values) < 2:
            return 0.0  # Only one preference = not diverse

        # Calculate standard deviation
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)

        # Normalize to 0-1 range (higher std_dev = more diverse)
        # Maximum possible std_dev is around 0.5 for our 0-1 range
        diversity = min(std_dev * 2, 1.0)

        return diversity

    def get_personalization_summary(self, drama: Dict) -> str:
        """
        Get a human-readable summary of why this drama was boosted.

        Args:
            drama: Drama with boost_details

        Returns:
            Summary string
        """
        if "boost_details" not in drama:
            return "Standard recommendation"

        boost_details = drama["boost_details"]
        total_boost = drama.get("boost_multiplier", 1.0)

        if total_boost <= 1.05:
            return "Standard recommendation"

        reasons = []

        # Genre boost
        if boost_details["genre"] > 0.1:
            reasons.append("matches your genre preferences")

        # Actor boost
        if boost_details["actor"] > 0.05:
            reasons.append("features your favorite actors")

        # Director boost
        if boost_details["director"] > 0.05:
            reasons.append("by a director you like")

        # Theme boost
        if boost_details["theme"] > 0.05:
            reasons.append("matches your interests")

        if not reasons:
            return "Recommended for you"

        if len(reasons) == 1:
            return f"Recommended because it {reasons[0]}"
        else:
            return f"Recommended because it {', '.join(reasons[:-1])} and {reasons[-1]}"


# Global instance
_personalization_engine = None


def get_personalization_engine() -> PersonalizationEngine:
    """Get global PersonalizationEngine instance"""
    global _personalization_engine
    if _personalization_engine is None:
        _personalization_engine = PersonalizationEngine()
    return _personalization_engine
