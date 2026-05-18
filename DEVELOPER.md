# Developer Guide

This guide explains how to work effectively with the HWA Untitled repository and its modular structure.

## Quick Start

1. **Read the documentation**:
   - [README.md](README.md) - Project overview and module descriptions
   - [Planning Doc.md](Planning%20Doc.md) - Detailed status, roadmap, and standards

2. **Set up your environment**:
   ```bash
   cd /mnt/c/Users/seant/repos/hwa-untitled
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or on Windows: .venv\Scripts\activate
   ```

3. **Navigate to your module**:
   ```bash
   cd card_scraper  # or whichever module you're working on
   pip install -r requirements.txt  # Install dependencies
   ```

## Working on Modules

### Before Starting

1. **Update Planning Doc.md**:
   - Mark your work section as "In Progress"
   - Add any notes about your approach
   - Document any blockers or dependencies

2. **Understand module boundaries**:
   - Each module is independent with its own dependencies
   - Use standardized data formats (CSV, JSON, TSV) for inter-module communication
   - Minimal coupling is key

### Module Structure Template

```
module_name/
├── README.md                    # Module documentation
├── requirements.txt             # Python dependencies (or package.json for JS)
├── src/                         # Source code
│   └── main.py                  # Main module file
├── tests/                       # Tests for this module
├── data/                        # Sample/test data
│   └── sample_input.csv
└── docs/                        # Detailed documentation (if needed)
```

### Best Practices

1. **Test independently**: Each module should be independently runnable and testable
2. **Document APIs**: If your module provides an interface, document it clearly
3. **Use standard formats**: For inter-module communication, stick to the defined standards
4. **Version data**: If outputs change format, document the version
5. **Keep it simple**: Avoid unnecessary dependencies between modules

## Data Standards

### Card Data Format
All card data uses this standardized CSV/TSV format:
```
databaseID,name,imageUrl,cardBack,type,set,shardCost,barrier,presence,actionLimit
```

See [Planning Doc.md](Planning%20Doc.md#data-format-standards) for full specification.

## Workflow Examples

### Running the Card Scraper
```bash
cd card_scraper
source ../.venv/bin/activate
python main.py
```

### Planning a New Feature
1. Edit [Planning Doc.md](Planning%20Doc.md)
2. Add feature under the relevant module's "Current Progress" section
3. Start working on it
4. Update status as you progress

### Creating a New Module
1. Create the module folder: `mkdir new_module`
2. Copy the structure from another module's README
3. Create `README.md` explaining the module
4. Add to [Planning Doc.md](Planning%20Doc.md)
5. Update [README.md](README.md) if needed

## Inter-Module Communication

Modules are largely independent with minimal coupling:
- **Card Scraper**: Autonomous, outputs CSV/TSV to file system
- **Card Query Service**: Pulls from internal data resource
- **Web App**: Standalone UI
- **Event Backend**: Independent collection service
- **Discord Bot**: Consumes Card Scraper output for card data

Modules that do communicate use:
- **Files**: CSV, JSON, TSV files in standardized formats
- **APIs**: REST endpoints (when modules are more mature)
- **Queues**: Event queues (Event Backend to other services)

Example data flow:
```
Card Scraper (DeckSmith) → CSV files
Card Query Service (Internal) → REST API
Discord Bot ← consumes Card Scraper output
```

## Repository Guidelines

### Commits
- Update [Planning Doc.md](Planning%20Doc.md) when changing project direction
- Reference which module in commit messages: `[card_scraper] Add image downloading`
- Keep commits focused on one module when possible

### Git Structure
- Keep each module's code contained in its folder
- Shared utilities go in a top-level `shared/` or `utils/` folder (if needed)
- Never commit large data files; use `.gitignore` for them

## Spinning Off a Module

When a module is ready to be its own repository:

1. **Verify it's self-contained**:
   - All code is in the module folder
   - All dependencies are listed in requirements.txt or package.json
   - Module has comprehensive README and docs

2. **Create new repository**:
   ```bash
   git init new-module-repo
   # Copy module files
   git remote add origin https://github.com/...
   ```

3. **Update this repository**:
   - Remove module folder
   - Add as git submodule or external dependency
   - Update [Planning Doc.md](Planning%20Doc.md) with spinoff status
   - Update [README.md](README.md) with reference to external repo

4. **Maintain compatibility**:
   - Keep using standardized data formats
   - Document API changes

## Troubleshooting

### Module has unmet dependencies
- Check `requirements.txt` or `package.json`
- Ensure virtual environment is activated
- Try `pip install --upgrade pip` then reinstall

### Data format incompatibility
- Verify against [Planning Doc.md](Planning%20Doc.md#data-format-standards)
- Check sample data files in module's `data/` folder
- Update module to conform to standard

### Not sure what to work on next
- Check [Planning Doc.md](Planning%20Doc.md) under "Active Work" and "Next Up"
- Look for sections marked "Not Started" (☐)

## Getting Help

1. Check the README for the specific module you're working on
2. Review [Planning Doc.md](Planning%20Doc.md) for context
3. Look at sample data files in module's `data/` folder
4. Review recent commits for similar work

## Contact & Collaboration

When working on a module:
- Update [Planning Doc.md](Planning%20Doc.md) to indicate active work
- Mark sections as "In Progress" to prevent duplicate effort
- Document any discoveries or learnings
