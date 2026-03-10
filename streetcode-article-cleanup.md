---
name: streetcode-article-cleanup
description: Clean up non-crime articles from Streetcode that were imported before classifier tuning
---

# Streetcode Article Cleanup

Use this skill to identify and soft-delete non-crime articles from Streetcode.

## Prerequisites

- SSH access to `deployer@streetcode.net`
- Working directory: `~/streetcode-laravel/current`

## Workflow

### 1. Audit Current State

```bash
ssh deployer@streetcode.net "cd ~/streetcode-laravel/current && php artisan tinker --execute=\"
use App\\Models\\Article;

echo 'Active articles: ' . Article::count() . PHP_EOL;
echo 'Soft-deleted: ' . Article::onlyTrashed()->count() . PHP_EOL;

// Check is_crime_related distribution
\\\$articles = Article::all();
\\\$crimeTrue = \\\$crimeFalse = 0;
foreach (\\\$articles as \\\$a) {
    if ((\\\$a->metadata['is_crime_related'] ?? false) === true) \\\$crimeTrue++;
    else \\\$crimeFalse++;
}
echo 'is_crime_related=true: ' . \\\$crimeTrue . PHP_EOL;
echo 'is_crime_related=false: ' . \\\$crimeFalse . PHP_EOL;
\""
```

### 2. Categorize by Keywords

Use aggressive keyword matching - articles without crime keywords get deleted:

```bash
ssh deployer@streetcode.net "cd ~/streetcode-laravel/current && php artisan tinker --execute=\"
use App\\Models\\Article;

\\\$crimeKeywords = ['murder', 'killed', 'killing', 'shot', 'shooting', 'stabbed', 'assault', 'robbery', 'theft', 'stolen', 'arrest', 'charged', 'prison', 'jail', 'homicide', 'manslaughter', 'rape', 'sexual assault', 'extortion', 'fraud', 'crime', 'criminal', 'police', 'detained', 'violence', 'violent', 'drug trafficking', 'smuggling', 'impaired', 'firearm', 'weapon', 'hostage', 'kidnap', 'burglary', 'arson', 'vandal', 'hit-and-run', 'fatally', 'victim', 'suspect', 'offender', 'probation', 'parole', 'sentence', 'convicted', 'guilty', 'indicted', 'gunman', 'shooter', 'attack', 'beaten', 'siu', 'opp', 'rcmp', 'fbi', 'custody', 'warrant', 'wanted', 'fugitive', 'trafficking', 'dealer', 'fentanyl', 'cocaine', 'opioid', 'overdose', 'death', 'dies', 'died', 'fatal', 'collision', 'crash', 'defamation', 'lawsuit', 'court', 'judge', 'trial', 'testimony', 'witness', 'prosecutor', 'contempt', 'illegal', 'investigation', 'abuse', 'allegations', 'accused', 'charges', 'cops', 'clocked', 'isis', 'burning', 'conviction'];

\\\$articles = Article::all(['id', 'title']);
\\\$toCrime = \\\$toDelete = [];

foreach (\\\$articles as \\\$a) {
    \\\$t = strtolower(\\\$a->title);
    \\\$hasCrime = false;
    foreach (\\\$crimeKeywords as \\\$kw) {
        if (strpos(\\\$t, \\\$kw) !== false) { \\\$hasCrime = true; break; }
    }
    if (\\\$hasCrime) \\\$toCrime[] = \\\$a;
    else \\\$toDelete[] = \\\$a;
}

echo 'Crime (keep & mark): ' . count(\\\$toCrime) . PHP_EOL;
echo 'Non-crime (delete): ' . count(\\\$toDelete) . PHP_EOL;
echo PHP_EOL . '=== TO DELETE ===' . PHP_EOL;
foreach (\\\$toDelete as \\\$a) echo '[' . \\\$a->id . '] ' . \\\$a->title . PHP_EOL;
\""
```

### 3. Execute Cleanup

```bash
ssh deployer@streetcode.net "cd ~/streetcode-laravel/current && php artisan tinker --execute=\"
use App\\Models\\Article;

\\\$crimeKeywords = [/* same as above */];

\\\$articles = Article::all(['id', 'title', 'metadata']);
\\\$crimeIds = \\\$deleteIds = [];

foreach (\\\$articles as \\\$a) {
    \\\$t = strtolower(\\\$a->title);
    \\\$hasCrime = false;
    foreach (\\\$crimeKeywords as \\\$kw) {
        if (strpos(\\\$t, \\\$kw) !== false) { \\\$hasCrime = true; break; }
    }
    if (\\\$hasCrime) \\\$crimeIds[] = \\\$a->id;
    else \\\$deleteIds[] = \\\$a->id;
}

// Mark crime articles
foreach (Article::whereIn('id', \\\$crimeIds)->get() as \\\$article) {
    \\\$meta = \\\$article->metadata ?? [];
    \\\$meta['is_crime_related'] = true;
    \\\$article->metadata = \\\$meta;
    \\\$article->save();
}
echo 'Marked as crime: ' . count(\\\$crimeIds) . PHP_EOL;

// Delete non-crime
\\\$deleted = Article::whereIn('id', \\\$deleteIds)->delete();
echo 'Deleted: ' . \\\$deleted . PHP_EOL;
\""
```

### 4. Verify

```bash
ssh deployer@streetcode.net "cd ~/streetcode-laravel/current && php artisan tinker --execute=\"
use App\\Models\\Article;
echo 'Active: ' . Article::count() . PHP_EOL;
echo 'Deleted: ' . Article::onlyTrashed()->count() . PHP_EOL;
Article::inRandomOrder()->limit(10)->pluck('title')->each(fn(\\\$t) => print('  - ' . \\\$t . PHP_EOL));
\""
```

### 5. Recovery (If Needed)

```php
// Restore specific articles
Article::onlyTrashed()->whereIn('id', [123, 456])->restore();

// Restore all from recent cleanup
Article::onlyTrashed()
    ->where('deleted_at', '>=', now()->subHours(1))
    ->restore();
```

## Key Files

- `app/Models/Article.php` - Uses SoftDeletes trait
- `app/Jobs/ProcessIncomingArticle.php` - Stores metadata from North Cloud

## Notes

- **Be aggressive** - soft deletes are recoverable
- New imports from North Cloud should be trusted (classifier is being refined)
- This cleanup is for historical data imported before classifier was tuned
- Always mark clear crime articles with `is_crime_related=true`
