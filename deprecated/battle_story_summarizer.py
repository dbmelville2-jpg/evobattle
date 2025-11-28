"""
Battle Story Summarizer - Local battle narrative generation.

This module generates engaging story summaries from battle logs using
local text processing (no API calls required), capturing key events,
MVP creatures, alliances, betrayals, and dramatic moments.
"""

from typing import List, Optional, Dict, Any
import time
from enum import Enum
from dataclasses import dataclass, field
import os
import random


class StoryTone(Enum):
    """Narrative tone options for story generation."""
    SERIOUS = "serious"
    HEROIC = "heroic"
    COMEDIC = "comedic"
    DRAMATIC = "dramatic"
    DOCUMENTARY = "documentary"


@dataclass
class BattleStoryMetrics:
    """Metrics and statistics extracted from battle events."""
    duration_seconds: float = 0.0
    total_attacks: int = 0
    total_kills: int = 0
    total_births: int = 0
    total_damage_dealt: float = 0.0
    critical_hits: int = 0
    creatures_started: int = 0
    creatures_survived: int = 0
    resource_collections: int = 0
    key_moments: List[str] = field(default_factory=list)
    mvp_creatures: List[Dict[str, Any]] = field(default_factory=list)
    dramatic_events: List[str] = field(default_factory=list)


class BattleStoryGenerator:
    """
    Generates engaging story summaries from battle events and logs.
    
    Uses local text processing and templates to create narratives
    without requiring external API calls. Completely free to use.
    """
    
    def __init__(
        self,
        default_tone: StoryTone = StoryTone.DRAMATIC
    ):
        """
        Initialize the battle story generator.
        
        Args:
            default_tone: Default narrative tone
        """
        self.default_tone = default_tone
        
        # Event collection
        self.collected_events: List[Any] = []
        self.battle_logs: List[str] = []
        self.start_time: Optional[float] = None
        self.metrics = BattleStoryMetrics()
        
        # Track creature statistics
        self.creature_stats: Dict[str, Dict[str, Any]] = {}
    
    def start_collection(self):
        """Start collecting battle events for story generation."""
        self.collected_events = []
        self.battle_logs = []
        self.start_time = time.time()
        self.metrics = BattleStoryMetrics()
    
    def add_event(self, event: Any):
        """Add a battle event to the collection."""
        self.collected_events.append(event)
        
        # Update metrics based on event type
        if hasattr(event, 'event_type'):
            event_type = str(event.event_type.value) if hasattr(event.event_type, 'value') else str(event.event_type)
            
            # Track creature-specific stats
            if hasattr(event, 'actor') and event.actor:
                actor_name = event.actor.creature.name if hasattr(event.actor, 'creature') else str(event.actor)
                if actor_name not in self.creature_stats:
                    self.creature_stats[actor_name] = {
                        'attacks': 0, 'damage': 0, 'kills': 0, 'deaths': 0, 'crits': 0
                    }
            
            if event_type == 'ability_use':
                self.metrics.total_attacks += 1
                if hasattr(event, 'actor') and event.actor:
                    actor_name = event.actor.creature.name if hasattr(event.actor, 'creature') else str(event.actor)
                    self.creature_stats[actor_name]['attacks'] += 1
                    
            elif event_type == 'damage_dealt':
                if hasattr(event, 'value') and event.value:
                    self.metrics.total_damage_dealt += event.value
                    if hasattr(event, 'actor') and event.actor:
                        actor_name = event.actor.creature.name if hasattr(event.actor, 'creature') else str(event.actor)
                        self.creature_stats[actor_name]['damage'] += event.value
                        
            elif event_type == 'critical_hit':
                self.metrics.critical_hits += 1
                if hasattr(event, 'actor') and event.actor:
                    actor_name = event.actor.creature.name if hasattr(event.actor, 'creature') else str(event.actor)
                    self.creature_stats[actor_name]['crits'] += 1
                    
            elif event_type in ['creature_death', 'creature_faint']:
                self.metrics.total_kills += 1
                if hasattr(event, 'message'):
                    self.metrics.dramatic_events.append(event.message)
                if hasattr(event, 'target') and event.target:
                    target_name = event.target.creature.name if hasattr(event.target, 'creature') else str(event.target)
                    if target_name not in self.creature_stats:
                        self.creature_stats[target_name] = {
                            'attacks': 0, 'damage': 0, 'kills': 0, 'deaths': 0, 'crits': 0
                        }
                    self.creature_stats[target_name]['deaths'] += 1
                if hasattr(event, 'actor') and event.actor:
                    actor_name = event.actor.creature.name if hasattr(event.actor, 'creature') else str(event.actor)
                    self.creature_stats[actor_name]['kills'] += 1
                    
            elif event_type == 'creature_birth':
                self.metrics.total_births += 1
                if hasattr(event, 'message'):
                    self.metrics.key_moments.append(event.message)
            elif event_type == 'resource_collected':
                self.metrics.resource_collections += 1
    
    def add_log(self, log_message: str):
        """Add a battle log message to the collection."""
        self.battle_logs.append(log_message)
    
    def _extract_metrics_from_logs(self) -> BattleStoryMetrics:
        """Extract additional metrics from battle logs."""
        # Update duration if we have a start time
        if self.start_time:
            self.metrics.duration_seconds = time.time() - self.start_time
        
        # Analyze logs for additional patterns
        for log in self.battle_logs:
            log_lower = log.lower()
            
            # Detect dramatic moments
            if any(word in log_lower for word in ['comeback', 'reversal', 'betrayal', 'alliance']):
                self.metrics.key_moments.append(log)
            
            # Detect survival/last stand moments
            if 'survivor' in log_lower or 'last stand' in log_lower:
                self.metrics.dramatic_events.append(log)
        
        return self.metrics
    
    def _build_fallback_story(self, tone: StoryTone) -> str:
        """Build a basic story without AI when API is unavailable."""
        metrics = self._extract_metrics_from_logs()
        
        # Build story based on metrics
        story_lines = []
        
        # Title
        if tone == StoryTone.HEROIC:
            story_lines.append("⚔️ EPIC BATTLE CHRONICLE ⚔️\n")
        elif tone == StoryTone.COMEDIC:
            story_lines.append("🎭 THE RIDICULOUS ARENA TALES 🎭\n")
        elif tone == StoryTone.DOCUMENTARY:
            story_lines.append("📊 BATTLE ANALYSIS REPORT 📊\n")
        else:
            story_lines.append("⚡ BATTLE STORY ⚡\n")
        
    def _get_mvp_creatures(self) -> List[Dict[str, Any]]:
        """Identify MVP creatures based on performance."""
        mvps = []
        
        for name, stats in self.creature_stats.items():
            score = stats['damage'] * 1.0 + stats['kills'] * 50 + stats['crits'] * 10
            if score > 0:
                mvps.append({
                    'name': name,
                    'score': score,
                    'damage': stats['damage'],
                    'kills': stats['kills'],
                    'crits': stats['crits'],
                    'deaths': stats['deaths']
                })
        
        # Sort by score
        mvps.sort(key=lambda x: x['score'], reverse=True)
        return mvps[:3]  # Top 3
    
    def _build_narrative_story(self, tone: StoryTone) -> str:
        """Build an engaging narrative story using local text generation."""
        metrics = self._extract_metrics_from_logs()
        mvps = self._get_mvp_creatures()
        
        # Story templates by tone
        story_parts = []
        
        # === OPENING ===
        duration_min = int(metrics.duration_seconds // 60)
        duration_sec = int(metrics.duration_seconds % 60)
        
        openings = {
            StoryTone.HEROIC: [
                f"⚔️ **LEGENDS OF THE ARENA** ⚔️\n\nIn an epic clash spanning {duration_min} minutes and {duration_sec} seconds, warriors of renown gathered to test their mettle in glorious combat.",
                f"⚔️ **TALES OF VALOR** ⚔️\n\nFrom across the realm they came, {self.metrics.creatures_started} brave souls seeking honor and glory in {duration_min} minutes of legendary battle.",
            ],
            StoryTone.DRAMATIC: [
                f"⚡ **THE ARENA REMEMBERS** ⚡\n\nBlood and steel met in a {duration_min}-minute battle that would echo through eternity. What transpired would change these warriors forever.",
                f"⚡ **SHADOWS OF CONFLICT** ⚡\n\nIn {duration_min} minutes and {duration_sec} seconds, the arena bore witness to a struggle that pushed warriors to their breaking points.",
            ],
            StoryTone.COMEDIC: [
                f"🎭 **CHAOS IN THE ARENA** 🎭\n\nWell, this was supposed to be an organized battle. It lasted {duration_min} minutes, but calling it 'organized' might be generous.",
                f"🎭 **THE HILARIOUS CHRONICLES** 🎭\n\nFor {duration_min} gloriously chaotic minutes, our 'warriors' demonstrated that sometimes enthusiasm outpaces skill.",
            ],
            StoryTone.SERIOUS: [
                f"📋 **COMBAT REPORT** 📋\n\nEngagement duration: {duration_min}m {duration_sec}s. Combatants: {self.metrics.creatures_started}. Analysis follows.",
                f"📋 **BATTLEFIELD ANALYSIS** 📋\n\nCombat initiated. Duration: {duration_min} minutes, {duration_sec} seconds. Participant count: {self.metrics.creatures_started}.",
            ],
            StoryTone.DOCUMENTARY: [
                f"📊 **ARENA ECOLOGY STUDY** 📊\n\nHere in their natural habitat, we observe {self.metrics.creatures_started} specimens engaging in territorial combat over a {duration_min}-minute period.",
                f"📊 **BEHAVIORAL OBSERVATION** 📊\n\nField study: {duration_min} minutes. Subjects: {self.metrics.creatures_started} individuals. Environmental stress: extreme.",
            ],
        }
        
        story_parts.append(random.choice(openings.get(tone, openings[StoryTone.DRAMATIC])))
        
        # === BATTLE STATISTICS NARRATIVE ===
        if metrics.total_attacks > 0:
            stats_narrative = {
                StoryTone.HEROIC: f"\n\nThe warriors clashed {metrics.total_attacks} times, their mighty blows dealing {metrics.total_damage_dealt:.0f} damage total. {metrics.critical_hits} strikes found critical weaknesses, each one a testament to skill and fortune.",
                StoryTone.DRAMATIC: f"\n\nThrough {metrics.total_attacks} brutal exchanges, {metrics.total_damage_dealt:.0f} points of damage painted the arena red. {metrics.critical_hits} critical strikes changed the course of battle in an instant.",
                StoryTone.COMEDIC: f"\n\nOur 'fighters' swung wildly {metrics.total_attacks} times, somehow managing {metrics.total_damage_dealt:.0f} damage (most of it accidental). {metrics.critical_hits} hits were actually intentional!",
                StoryTone.SERIOUS: f"\n\nEngagement count: {metrics.total_attacks}. Total damage output: {metrics.total_damage_dealt:.0f}. Critical hits recorded: {metrics.critical_hits}.",
                StoryTone.DOCUMENTARY: f"\n\nAggression displays numbered {metrics.total_attacks}, with cumulative damage reaching {metrics.total_damage_dealt:.0f} units. Precision strikes: {metrics.critical_hits}.",
            }
            story_parts.append(stats_narrative.get(tone, stats_narrative[StoryTone.DRAMATIC]))
        
        # === MVP SECTION ===
        if mvps:
            mvp = mvps[0]
            # Prepare comedic text without nested quotes
            comedic_skill = "Beginner's luck, surely!" if mvp['crits'] < 2 else "They might actually know what they're doing!"
            
            mvp_narrative = {
                StoryTone.HEROIC: f"\n\n**HERO OF THE HOUR**: {mvp['name']} emerged as the champion, their blade singing through the arena with {mvp['damage']:.0f} damage dealt and {mvp['kills']} foes vanquished. {'A true legend in the making!' if mvp['crits'] > 2 else 'Their prowess was unmatched.'}",
                StoryTone.DRAMATIC: f"\n\nAmidst the chaos, one name rose above all others: **{mvp['name']}**. {mvp['damage']:.0f} damage. {mvp['kills']} kills. {mvp['crits']} critical strikes. Their story would not be forgotten.",
                StoryTone.COMEDIC: f"\n\n**MVP (Most Violent Participant)**: {mvp['name']} somehow managed {mvp['damage']:.0f} damage and {mvp['kills']} {'knockouts' if mvp['kills'] > 1 else 'knockout'}. {comedic_skill}",
                StoryTone.SERIOUS: f"\n\n**TOP PERFORMER**: {mvp['name']}. Damage output: {mvp['damage']:.0f}. Eliminations: {mvp['kills']}. Critical strike rate: {mvp['crits']}.",
                StoryTone.DOCUMENTARY: f"\n\nThe alpha specimen, **{mvp['name']}**, demonstrated superior fitness with {mvp['damage']:.0f} damage output and {mvp['kills']} successful eliminations.",
            }
            story_parts.append(mvp_narrative.get(tone, mvp_narrative[StoryTone.DRAMATIC]))
        
        # === CASUALTIES AND BIRTHS ===
        if metrics.total_kills > 0 or metrics.total_births > 0:
            lifecycle_narrative = {
                StoryTone.HEROIC: f"\n\nThe price of glory was steep: {metrics.total_kills} brave warriors fell in combat{'.' if metrics.total_births == 0 else f', yet hope endured as {metrics.total_births} new life emerged from the struggle.'}",
                StoryTone.DRAMATIC: f"\n\n{metrics.total_kills} warriors met their end in the arena's embrace{', their sacrifice not in vain' if metrics.total_births > 0 else ', leaving only echoes'}.{f' Yet from loss came renewal: {metrics.total_births} born amid the carnage.' if metrics.total_births > 0 else ''}",
                StoryTone.COMEDIC: f"\n\n{metrics.total_kills} participants 'took a nap' (permanently){', but hey, ' + str(metrics.total_births) + ' new ones showed up! The cycle continues!' if metrics.total_births > 0 else '. Someone should probably call their families.'}",
                StoryTone.SERIOUS: f"\n\nCasualty count: {metrics.total_kills}. {f'New arrivals: {metrics.total_births}.' if metrics.total_births > 0 else 'No reinforcements.'}",
                StoryTone.DOCUMENTARY: f"\n\nPopulation attrition: {metrics.total_kills} individuals. {f'Reproduction events: {metrics.total_births}. Population dynamics remain active.' if metrics.total_births > 0 else 'No offspring observed.'}",
            }
            story_parts.append(lifecycle_narrative.get(tone, lifecycle_narrative[StoryTone.DRAMATIC]))
        
        # === KEY MOMENTS ===
        if metrics.key_moments:
            moment = metrics.key_moments[0]  # Pick first major moment
            story_parts.append(f"\n\n**Turning Point**: {moment}")
        
        # === DRAMATIC EVENTS ===
        if metrics.dramatic_events and len(metrics.dramatic_events) > 0:
            event = metrics.dramatic_events[0]
            story_parts.append(f"\n\n**Most Dramatic Moment**: {event}")
        
        # === CLOSING ===
        # Prepare comedic text without nested quotes
        comedic_remember = "! They probably won't remember how" if metrics.creatures_survived > 0 else ', which is honestly for the best'
        
        closings = {
            StoryTone.HEROIC: f"\n\nWhen the dust settled, {metrics.creatures_survived if metrics.creatures_survived > 0 else 'none'} {'heroes stood victorious' if metrics.creatures_survived > 1 else 'hero remained'}, their names forever etched in the annals of arena legend. Their deeds shall be sung for generations!",
            StoryTone.DRAMATIC: f"\n\nAs silence fell over the battlefield, {metrics.creatures_survived if metrics.creatures_survived > 0 else 'no one'} remained standing{' among the fallen' if metrics.creatures_survived > 0 else ', only memory and shadow'}. The arena had claimed its toll, and the survivors would carry these scars forever.",
            StoryTone.COMEDIC: f"\n\nSomehow, {metrics.creatures_survived if metrics.creatures_survived > 0 else 'nobody'} survived this mess{comedic_remember}. Same time next week?",
            StoryTone.SERIOUS: f"\n\nCombat concluded. Survivors: {metrics.creatures_survived if metrics.creatures_survived > 0 else 0}. Mission {' complete' if metrics.creatures_survived > 0 else 'failed'}.",
            StoryTone.DOCUMENTARY: f"\n\nPost-conflict census: {metrics.creatures_survived if metrics.creatures_survived > 0 else 0} surviving specimens. Natural selection pressure: extreme. Study concluded.",
        }
        
        story_parts.append(closings.get(tone, closings[StoryTone.DRAMATIC]))
        
        # === FOOTER ===
        footer = f"\n\n---\n📊 Battle Summary: {duration_min}m {duration_sec}s | {metrics.total_attacks} attacks | {metrics.total_kills} casualties | {metrics.total_births} births"
        story_parts.append(footer)
        
        return "".join(story_parts)
    
    def generate_story(
        self,
        tone: Optional[StoryTone] = None
    ) -> str:
        """
        Generate an engaging story from collected events using local processing.
        
        Args:
            tone: Narrative tone (uses default if not specified)
            
        Returns:
            Generated story as a string
        """
        tone = tone or self.default_tone
        return self._build_narrative_story(tone)
    
    def export_story(self, story: str, filepath: str, format: str = 'txt'):
        """
        Export story to a file.
        
        Args:
            story: The story text to export
            filepath: Path to save the file
            format: Export format ('txt' or 'md')
        """
        if format == 'md':
            # Add markdown formatting
            story = f"# Battle Story\n\n{story}\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(story)


class BattleStoryTracker:
    """
    Tracks battle progress and triggers story generation at intervals.
    
    Integrates with SpatialBattle to automatically collect events and
    generate stories at configurable time windows.
    """
    
    def __init__(
        self,
        generator: BattleStoryGenerator,
        story_interval_seconds: float = 300.0  # 5 minutes default
    ):
        """
        Initialize the battle story tracker.
        
        Args:
            generator: BattleStoryGenerator instance
            story_interval_seconds: Time between story generations
        """
        self.generator = generator
        self.story_interval = story_interval_seconds
        self.last_story_time: float = 0.0
        self.stories: List[Dict[str, Any]] = []
        self.is_tracking = False
    
    def start_tracking(self):
        """Start tracking battle events."""
        self.is_tracking = True
        self.last_story_time = time.time()
        self.generator.start_collection()
    
    def stop_tracking(self):
        """Stop tracking battle events."""
        self.is_tracking = False
    
    def should_generate_story(self) -> bool:
        """Check if it's time to generate a new story."""
        if not self.is_tracking:
            return False
        
        current_time = time.time()
        elapsed = current_time - self.last_story_time
        return elapsed >= self.story_interval
    
    def generate_and_store_story(self, tone: Optional[StoryTone] = None) -> str:
        """
        Generate a story and store it in the history.
        
        Args:
            tone: Narrative tone for the story
            
        Returns:
            Generated story text
        """
        story = self.generator.generate_story(tone=tone)
        
        self.stories.append({
            'timestamp': time.time(),
            'story': story,
            'tone': tone or self.generator.default_tone,
            'metrics': self.generator.metrics
        })
        
        # Reset for next interval
        self.last_story_time = time.time()
        self.generator.start_collection()
        
        return story
    
    def get_all_stories(self) -> List[Dict[str, Any]]:
        """Get all generated stories."""
        return self.stories
    
    def export_all_stories(self, directory: str, format: str = 'txt'):
        """
        Export all stories to files.
        
        Args:
            directory: Directory to save stories
            format: Export format ('txt' or 'md')
        """
        os.makedirs(directory, exist_ok=True)
        
        for i, story_data in enumerate(self.stories):
            filename = f"battle_story_{i+1}.{format}"
            filepath = os.path.join(directory, filename)
            self.generator.export_story(story_data['story'], filepath, format)
