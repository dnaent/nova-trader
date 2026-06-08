// Nova Trader - Capital Deployment Timeline System
// References all portfolio data from crypto/, forex/, gia/, isa/, and sipp/ folders

// Portfolio Data Structure (Based on actual folder contents)
const PORTFOLIO_DATA = {
    isa: {
        name: "ISA Portfolio",
        nickname: "The Aeroplane",
        currentValue: 11500,
        targetValue: 20000,
        riskLevel: "Moderate",
        timeHorizon: "5-10 years",
        taxStatus: "Tax-Free",
        strategy: "AI infrastructure focus with dividend aristocrats"
    },
    sipp: {
        name: "SIPP Portfolio",
        nickname: "The Pension Fortress",
        currentValue: 20372,
        targetValue: 45000,
        riskLevel: "High",
        timeHorizon: "25 years",
        taxStatus: "Pension Wrapper",
        strategy: "Critical minerals and long-term compounding"
    },
    gia: {
        name: "GIA Portfolio",
        nickname: "The Rocket Ship",
        currentValue: 27000,
        targetValue: 50000,
        riskLevel: "Aggressive",
        timeHorizon: "3-7 years",
        taxStatus: "Taxable",
        strategy: "US growth stocks with maximum flexibility"
    },
    crypto: {
        name: "Crypto Portfolio",
        nickname: "The Digital Arsenal",
        currentValue: 10500,
        targetValue: 25000,
        riskLevel: "Very High",
        timeHorizon: "10 years",
        taxStatus: "CGT Liable",
        strategy: "10-year conviction blockchain infrastructure plays"
    },
    energy: {
        name: "Energy Matrix",
        nickname: "Geopolitical Arbitrage",
        currentValue: 10000,
        targetValue: 15000,
        riskLevel: "High",
        timeHorizon: "6-18 months",
        taxStatus: "CGT Liable",
        strategy: "Oil spike and geopolitical catalyst opportunities"
    },
    speculative: {
        name: "Speculative Plays",
        nickname: "Asymmetric Opportunities",
        currentValue: 6300,
        targetValue: 12000,
        riskLevel: "Extreme",
        timeHorizon: "1-3 years",
        taxStatus: "CGT Liable",
        strategy: "High-risk, high-reward moonshot investments"
    }
};

// Comprehensive Capital Deployment Timeline Data (2026-2030)
const DEPLOYMENT_TIMELINE = {
    2026: {
        Q1: {
            totalDeployment: 24247,
            activeCatalysts: 23,
            expectedReturn: 27.4,
            riskLevel: "Moderate-High",
            deployments: {
                isa: {
                    amount: 3500,
                    change: "+£1,200",
                    catalysts: [
                        {
                            event: "AI Infrastructure ETF Launch",
                            probability: 0.85,
                            impact: "+15-25%",
                            description: "Major ETF launch focusing on AI data center infrastructure, perfectly aligned with our AI strategy",
                            timeline: "March 2026"
                        },
                        {
                            event: "UK Dividend Tax Changes",
                            probability: 0.6,
                            impact: "+5-8%",
                            description: "Potential changes to dividend taxation favoring ISA-held dividend aristocrats",
                            timeline: "April 2026"
                        }
                    ]
                },
                sipp: {
                    amount: 6500,
                    change: "+£2,800",
                    catalysts: [
                        {
                            event: "Critical Minerals Supply Shortage",
                            probability: 0.78,
                            impact: "+35-60%",
                            description: "Supply chain disruptions in lithium and rare earth elements driving strategic materials premium",
                            timeline: "February 2026"
                        },
                        {
                            event: "Green Infrastructure Investment",
                            probability: 0.72,
                            impact: "+20-30%",
                            description: "Major government infrastructure spending on renewable energy projects",
                            timeline: "March 2026"
                        }
                    ]
                },
                gia: {
                    amount: 8200,
                    change: "+£3,100",
                    catalysts: [
                        {
                            event: "US Tech Earnings Surge",
                            probability: 0.82,
                            impact: "+25-40%",
                            description: "Q1 2026 tech earnings expected to show AI revenue acceleration across growth stocks",
                            timeline: "January-March 2026"
                        },
                        {
                            event: "Emerging Markets Recovery",
                            probability: 0.65,
                            impact: "+18-28%",
                            description: "Post-pandemic emerging markets showing strong GDP recovery signals",
                            timeline: "February 2026"
                        }
                    ]
                },
                crypto: {
                    amount: 2800,
                    change: "+£1,400",
                    catalysts: [
                        {
                            event: "Bitcoin ETF Institutional Adoption",
                            probability: 0.91,
                            impact: "+50-80%",
                            description: "Major institutional ETF adoption driving Bitcoin infrastructure demand",
                            timeline: "March 2026"
                        },
                        {
                            event: "DeFi Protocol Upgrades",
                            probability: 0.73,
                            impact: "+30-45%",
                            description: "Major DeFi protocols launching scalability upgrades improving yield opportunities",
                            timeline: "February 2026"
                        }
                    ]
                },
                energy: {
                    amount: 2500,
                    change: "+£800",
                    catalysts: [
                        {
                            event: "Middle East Tensions Escalation",
                            probability: 0.67,
                            impact: "+40-70%",
                            description: "Geopolitical tensions potentially disrupting oil supply chains, benefiting non-Gulf producers",
                            timeline: "January-March 2026"
                        },
                        {
                            event: "Strategic Petroleum Reserve Release",
                            probability: 0.54,
                            impact: "-10% to +15%",
                            description: "Government SPR releases could temporarily impact oil prices before driving scarcity premium",
                            timeline: "February 2026"
                        }
                    ]
                },
                speculative: {
                    amount: 747,
                    change: "+£400",
                    catalysts: [
                        {
                            event: "Biotech Breakthrough Announcement",
                            probability: 0.35,
                            impact: "+200-500%",
                            description: "Early-stage biotech companies showing promising Phase II trial results",
                            timeline: "March 2026"
                        },
                        {
                            event: "Space Technology IPOs",
                            probability: 0.28,
                            impact: "+150-300%",
                            description: "Commercial space technology companies preparing for public market debuts",
                            timeline: "January 2026"
                        }
                    ]
                }
            }
        },
        Q2: {
            totalDeployment: 28450,
            activeCatalysts: 27,
            expectedReturn: 32.1,
            riskLevel: "High",
            deployments: {
                isa: {
                    amount: 4200,
                    change: "+£2,100",
                    catalysts: [
                        {
                            event: "AI Chip Manufacturing Scale-Up",
                            probability: 0.88,
                            impact: "+20-35%",
                            description: "Major semiconductor manufacturers ramping AI chip production, benefiting infrastructure ETFs",
                            timeline: "April-June 2026"
                        },
                        {
                            event: "ISA Allowance Increase",
                            probability: 0.45,
                            impact: "+3-5%",
                            description: "Potential government increase to ISA allowance limits in budget announcement",
                            timeline: "May 2026"
                        }
                    ]
                },
                sipp: {
                    amount: 8100,
                    change: "+£3,200",
                    catalysts: [
                        {
                            event: "Rare Earth Processing Facility Approval",
                            probability: 0.82,
                            impact: "+45-75%",
                            description: "New rare earth processing facilities approved in allied nations, reducing China dependency",
                            timeline: "May 2026"
                        },
                        {
                            event: "Nuclear Energy Renaissance",
                            probability: 0.76,
                            impact: "+25-40%",
                            description: "Small modular reactor approvals accelerating nuclear infrastructure investment",
                            timeline: "June 2026"
                        }
                    ]
                },
                gia: {
                    amount: 9800,
                    change: "+£4,100",
                    catalysts: [
                        {
                            event: "AI Revenue Recognition Standards",
                            probability: 0.79,
                            impact: "+30-50%",
                            description: "New accounting standards for AI revenue boosting tech company reported earnings",
                            timeline: "April 2026"
                        },
                        {
                            event: "Small-Cap Growth Fund Inflows",
                            probability: 0.71,
                            impact: "+22-38%",
                            description: "Major institutional rotation into small-cap growth driving performance",
                            timeline: "May-June 2026"
                        }
                    ]
                },
                crypto: {
                    amount: 3200,
                    change: "+£1,800",
                    catalysts: [
                        {
                            event: "Ethereum Scaling Solution Deployment",
                            probability: 0.86,
                            impact: "+60-90%",
                            description: "Major Ethereum scaling solutions going live, reducing transaction costs dramatically",
                            timeline: "April 2026"
                        },
                        {
                            event: "Central Bank Digital Currency Integration",
                            probability: 0.58,
                            impact: "+40-65%",
                            description: "CBDC integration with existing crypto infrastructure creating new use cases",
                            timeline: "June 2026"
                        }
                    ]
                },
                energy: {
                    amount: 2700,
                    change: "+£1,200",
                    catalysts: [
                        {
                            event: "Summer Driving Season Demand",
                            probability: 0.92,
                            impact: "+25-40%",
                            description: "Peak summer driving season combined with limited refinery capacity driving margins",
                            timeline: "May-June 2026"
                        },
                        {
                            event: "Hurricane Season Oil Platform Disruption",
                            probability: 0.63,
                            impact: "+20-60%",
                            description: "Atlantic hurricane season potentially disrupting Gulf oil production platforms",
                            timeline: "June 2026"
                        }
                    ]
                },
                speculative: {
                    amount: 650,
                    change: "+£350",
                    catalysts: [
                        {
                            event: "Quantum Computing Milestone",
                            probability: 0.42,
                            impact: "+300-800%",
                            description: "Major quantum computing breakthrough demonstrating commercial viability",
                            timeline: "May 2026"
                        },
                        {
                            event: "Metaverse Hardware Launch",
                            probability: 0.38,
                            impact: "+180-400%",
                            description: "Next-generation metaverse hardware creating new ecosystem opportunities",
                            timeline: "June 2026"
                        }
                    ]
                }
            }
        },
        Q3: {
            totalDeployment: 31850,
            activeCatalysts: 31,
            expectedReturn: 38.7,
            riskLevel: "High",
            deployments: {
                isa: {
                    amount: 4800,
                    change: "+£2,400",
                    catalysts: [
                        {
                            event: "Data Center REIT Spin-offs",
                            probability: 0.84,
                            impact: "+28-45%",
                            description: "Major tech companies spinning off data center assets into REITs for AI infrastructure focus",
                            timeline: "July-September 2026"
                        },
                        {
                            event: "UK Pension Auto-Enrollment Changes",
                            probability: 0.67,
                            impact: "+8-12%",
                            description: "Pension reforms potentially increasing ISA attractiveness for retirement planning",
                            timeline: "August 2026"
                        }
                    ]
                },
                sipp: {
                    amount: 9400,
                    change: "+£3,800",
                    catalysts: [
                        {
                            event: "Battery Technology Breakthrough",
                            probability: 0.79,
                            impact: "+50-85%",
                            description: "Solid-state battery breakthrough requiring critical mineral supply chain ramp-up",
                            timeline: "August 2026"
                        },
                        {
                            event: "Grid Storage Infrastructure Investment",
                            probability: 0.81,
                            impact: "+35-55%",
                            description: "Massive grid-scale storage infrastructure investment driving demand for storage materials",
                            timeline: "September 2026"
                        }
                    ]
                },
                gia: {
                    amount: 11200,
                    change: "+£4,600",
                    catalysts: [
                        {
                            event: "AI Regulatory Clarity",
                            probability: 0.75,
                            impact: "+25-42%",
                            description: "Clear AI regulation framework removing uncertainty and enabling growth investment",
                            timeline: "July 2026"
                        },
                        {
                            event: "Emerging Market Currency Stabilization",
                            probability: 0.68,
                            impact: "+20-35%",
                            description: "EM currency volatility reducing, attracting international investment flows",
                            timeline: "August-September 2026"
                        }
                    ]
                },
                crypto: {
                    amount: 3600,
                    change: "+£2,100",
                    catalysts: [
                        {
                            event: "Institutional Custody Solutions",
                            probability: 0.87,
                            impact: "+70-120%",
                            description: "Major banks launching institutional-grade crypto custody driving adoption",
                            timeline: "July 2026"
                        },
                        {
                            event: "Real World Asset Tokenization",
                            probability: 0.74,
                            impact: "+45-80%",
                            description: "Large-scale real estate and commodity tokenization creating new DeFi markets",
                            timeline: "September 2026"
                        }
                    ]
                },
                energy: {
                    amount: 2200,
                    change: "+£900",
                    catalysts: [
                        {
                            event: "Refinery Maintenance Season",
                            probability: 0.95,
                            impact: "+15-30%",
                            description: "Annual refinery maintenance season reducing capacity during high demand period",
                            timeline: "August-September 2026"
                        },
                        {
                            event: "Strategic Reserve Stockpiling",
                            probability: 0.72,
                            impact: "+20-45%",
                            description: "Government strategic petroleum reserve restocking driving sustained demand",
                            timeline: "July-September 2026"
                        }
                    ]
                },
                speculative: {
                    amount: 650,
                    change: "+£250",
                    catalysts: [
                        {
                            event: "Gene Therapy Approval Wave",
                            probability: 0.31,
                            impact: "+400-1000%",
                            description: "Multiple gene therapy treatments receiving FDA approval creating sector momentum",
                            timeline: "September 2026"
                        },
                        {
                            event: "Fusion Energy Demonstration",
                            probability: 0.25,
                            impact: "+500-1500%",
                            description: "Commercial fusion energy demonstration achieving net energy gain",
                            timeline: "August 2026"
                        }
                    ]
                }
            }
        },
        Q4: {
            totalDeployment: 35200,
            activeCatalysts: 28,
            expectedReturn: 42.3,
            riskLevel: "High",
            deployments: {
                isa: {
                    amount: 5200,
                    change: "+£2,800",
                    catalysts: [
                        {
                            event: "Year-End Tax Planning Rush",
                            probability: 0.96,
                            impact: "+12-18%",
                            description: "Year-end ISA contributions driving inflows into tax-efficient AI infrastructure investments",
                            timeline: "October-December 2026"
                        },
                        {
                            event: "Semiconductor Fab Capacity Announcement",
                            probability: 0.78,
                            impact: "+22-38%",
                            description: "Major new semiconductor fabrication facilities announced for AI chip production",
                            timeline: "November 2026"
                        }
                    ]
                },
                sipp: {
                    amount: 10800,
                    change: "+£4,200",
                    catalysts: [
                        {
                            event: "COP Climate Accord Implementation",
                            probability: 0.83,
                            impact: "+40-70%",
                            description: "New climate accords accelerating critical minerals demand for clean technology",
                            timeline: "November 2026"
                        },
                        {
                            event: "Pension Contribution Deadline Rush",
                            probability: 0.92,
                            impact: "+15-25%",
                            description: "Year-end pension contribution deadline driving capital into long-term mineral plays",
                            timeline: "December 2026"
                        }
                    ]
                },
                gia: {
                    amount: 12400,
                    change: "+£5,100",
                    catalysts: [
                        {
                            event: "Tech IPO Window Opening",
                            probability: 0.77,
                            impact: "+35-55%",
                            description: "Market conditions improving for high-growth tech IPOs, lifting sector valuations",
                            timeline: "October-November 2026"
                        },
                        {
                            event: "Year-End Portfolio Rebalancing",
                            probability: 0.89,
                            impact: "+18-28%",
                            description: "Institutional year-end rebalancing favoring growth stocks with strong AI exposure",
                            timeline: "December 2026"
                        }
                    ]
                },
                crypto: {
                    amount: 4100,
                    change: "+£2,300",
                    catalysts: [
                        {
                            event: "Crypto Tax Clarity Legislation",
                            probability: 0.71,
                            impact: "+55-95%",
                            description: "Clear crypto taxation rules removing regulatory uncertainty for institutional adoption",
                            timeline: "October 2026"
                        },
                        {
                            event: "Corporate Treasury Bitcoin Adoption",
                            probability: 0.64,
                            impact: "+80-140%",
                            description: "More corporations adding Bitcoin to treasury reserves following institutional precedent",
                            timeline: "November-December 2026"
                        }
                    ]
                },
                energy: {
                    amount: 1900,
                    change: "+£600",
                    catalysts: [
                        {
                            event: "Winter Heating Demand Peak",
                            probability: 0.94,
                            impact: "+20-35%",
                            description: "Winter heating season driving natural gas and heating oil demand across northern markets",
                            timeline: "November-December 2026"
                        },
                        {
                            event: "OPEC+ Production Decision",
                            probability: 0.76,
                            impact: "+25-50%",
                            description: "OPEC+ year-end production decisions potentially constraining supply into 2027",
                            timeline: "December 2026"
                        }
                    ]
                },
                speculative: {
                    amount: 800,
                    change: "+£400",
                    catalysts: [
                        {
                            event: "Brain-Computer Interface Trial Results",
                            probability: 0.39,
                            impact: "+600-2000%",
                            description: "Clinical trial results for brain-computer interfaces showing breakthrough efficacy",
                            timeline: "December 2026"
                        },
                        {
                            event: "Asteroid Mining Technology Demo",
                            probability: 0.22,
                            impact: "+1000-5000%",
                            description: "Successful demonstration of asteroid mining technology for rare earth extraction",
                            timeline: "November 2026"
                        }
                    ]
                }
            }
        }
    },
    2027: {
        Q1: {
            totalDeployment: 38900,
            activeCatalysts: 26,
            expectedReturn: 31.8,
            riskLevel: "Moderate-High",
            deployments: {
                isa: {
                    amount: 6200,
                    change: "+£3,400",
                    catalysts: [
                        {
                            event: "New ISA Allowance Year",
                            probability: 0.98,
                            impact: "+8-15%",
                            description: "Fresh ISA allowance deployment into mature AI infrastructure with established track record",
                            timeline: "January-March 2027"
                        },
                        {
                            event: "AI Data Center Energy Efficiency Standards",
                            probability: 0.81,
                            impact: "+25-40%",
                            description: "New energy efficiency standards favoring advanced data center infrastructure investments",
                            timeline: "February 2027"
                        }
                    ]
                },
                sipp: {
                    amount: 12100,
                    change: "+£4,800",
                    catalysts: [
                        {
                            event: "Critical Minerals Strategic Partnership",
                            probability: 0.86,
                            impact: "+45-75%",
                            description: "Western nations forming strategic critical minerals partnership reducing supply risk",
                            timeline: "January 2027"
                        },
                        {
                            event: "Clean Energy Infrastructure Bill",
                            probability: 0.74,
                            impact: "+30-50%",
                            description: "Major infrastructure legislation allocating funds for renewable energy mineral supply chain",
                            timeline: "March 2027"
                        }
                    ]
                },
                gia: {
                    amount: 13800,
                    change: "+£5,600",
                    catalysts: [
                        {
                            event: "AI Productivity Metrics Release",
                            probability: 0.88,
                            impact: "+32-48%",
                            description: "First comprehensive AI productivity impact data showing massive efficiency gains",
                            timeline: "February 2027"
                        },
                        {
                            event: "Emerging Market AI Adoption",
                            probability: 0.69,
                            impact: "+22-38%",
                            description: "Emerging markets rapidly adopting AI technology creating new growth markets",
                            timeline: "January-March 2027"
                        }
                    ]
                },
                crypto: {
                    amount: 4800,
                    change: "+£2,700",
                    catalysts: [
                        {
                            event: "DeFi 3.0 Protocol Launch",
                            probability: 0.82,
                            impact: "+85-150%",
                            description: "Next-generation DeFi protocols with institutional-grade security and compliance",
                            timeline: "March 2027"
                        },
                        {
                            event: "Cross-Chain Infrastructure Maturity",
                            probability: 0.79,
                            impact: "+60-110%",
                            description: "Cross-chain infrastructure reaching maturity enabling seamless multi-blockchain operations",
                            timeline: "February 2027"
                        }
                    ]
                },
                energy: {
                    amount: 1600,
                    change: "+£400",
                    catalysts: [
                        {
                            event: "Geopolitical Stability Premium",
                            probability: 0.58,
                            impact: "+15-25%",
                            description: "Reduced geopolitical tensions potentially normalizing energy markets with stability premium",
                            timeline: "January-March 2027"
                        },
                        {
                            event: "Alternative Energy Transition Acceleration",
                            probability: 0.76,
                            impact: "+10-30%",
                            description: "Accelerated transition to alternatives creating short-term supply-demand imbalances",
                            timeline: "February-March 2027"
                        }
                    ]
                },
                speculative: {
                    amount: 600,
                    change: "+£200",
                    catalysts: [
                        {
                            event: "Longevity Medicine Breakthrough",
                            probability: 0.44,
                            impact: "+400-1200%",
                            description: "Major breakthrough in longevity medicine showing significant life extension potential",
                            timeline: "March 2027"
                        },
                        {
                            event: "Autonomous Vehicle Full Deployment",
                            probability: 0.36,
                            impact: "+250-600%",
                            description: "First fully autonomous vehicle deployment in major metropolitan area",
                            timeline: "February 2027"
                        }
                    ]
                }
            }
        },
        Q2: {
            totalDeployment: 42100,
            activeCatalysts: 29,
            expectedReturn: 36.2,
            riskLevel: "High",
            deployments: {
                isa: {
                    amount: 7100,
                    change: "+£3,800",
                    catalysts: [
                        {
                            event: "Quantum Computing ETF Launch",
                            probability: 0.76,
                            impact: "+30-45%",
                            description: "First quantum computing focused ETF leveraging mature AI infrastructure networks",
                            timeline: "April-June 2027"
                        },
                        {
                            event: "Energy-Efficient Data Center Regulations",
                            probability: 0.83,
                            impact: "+22-35%",
                            description: "New regulations favoring next-generation energy-efficient data centers for AI workloads",
                            timeline: "May 2027"
                        }
                    ]
                },
                sipp: {
                    amount: 13600,
                    change: "+£5,200",
                    catalysts: [
                        {
                            event: "Lithium Processing Revolution",
                            probability: 0.84,
                            impact: "+55-90%",
                            description: "New lithium extraction and processing technology dramatically improving supply chain efficiency",
                            timeline: "April 2027"
                        },
                        {
                            event: "Space-Based Solar Infrastructure",
                            probability: 0.68,
                            impact: "+40-65%",
                            description: "First commercial space-based solar power infrastructure requiring advanced materials",
                            timeline: "June 2027"
                        }
                    ]
                },
                gia: {
                    amount: 15200,
                    change: "+£6,400",
                    catalysts: [
                        {
                            event: "AI Chip Architecture Breakthrough",
                            probability: 0.79,
                            impact: "+38-58%",
                            description: "Revolutionary AI chip architecture enabling 10x performance improvements in growth stocks",
                            timeline: "May 2027"
                        },
                        {
                            event: "Global Trade Agreement Tech Provisions",
                            probability: 0.71,
                            impact: "+25-42%",
                            description: "New international trade agreements with tech-favorable provisions boosting growth sectors",
                            timeline: "June 2027"
                        }
                    ]
                },
                crypto: {
                    amount: 5400,
                    change: "+£3,100",
                    catalysts: [
                        {
                            event: "Decentralized Identity Standard Adoption",
                            probability: 0.86,
                            impact: "+95-160%",
                            description: "Global adoption of decentralized identity standards driving infrastructure token demand",
                            timeline: "April 2027"
                        },
                        {
                            event: "AI-Powered Trading Protocol Launch",
                            probability: 0.77,
                            impact: "+70-120%",
                            description: "AI-powered trading protocols revolutionizing DeFi yield optimization strategies",
                            timeline: "May-June 2027"
                        }
                    ]
                },
                energy: {
                    amount: 1200,
                    change: "+£300",
                    catalysts: [
                        {
                            event: "Clean Energy Transition Acceleration",
                            probability: 0.82,
                            impact: "+20-35%",
                            description: "Accelerated clean energy transition creating temporary supply bottlenecks in traditional energy",
                            timeline: "April-June 2027"
                        },
                        {
                            event: "Carbon Credit Market Maturation",
                            probability: 0.75,
                            impact: "+15-28%",
                            description: "Mature carbon credit markets creating new value streams for energy producers",
                            timeline: "May 2027"
                        }
                    ]
                },
                speculative: {
                    amount: 600,
                    change: "+£200",
                    catalysts: [
                        {
                            event: "Synthetic Biology Commercial Success",
                            probability: 0.41,
                            impact: "+500-1500%",
                            description: "First major commercial synthetic biology applications achieving market success",
                            timeline: "June 2027"
                        },
                        {
                            event: "Neuromorphic Computing Breakthrough",
                            probability: 0.33,
                            impact: "+800-2500%",
                            description: "Neuromorphic computing achieving significant advantage over traditional processors",
                            timeline: "May 2027"
                        }
                    ]
                }
            }
        },
        Q3: {
            totalDeployment: 45800,
            activeCatalysts: 32,
            expectedReturn: 41.5,
            riskLevel: "High",
            deployments: {
                isa: {
                    amount: 8300,
                    change: "+£4,200",
                    catalysts: [
                        {
                            event: "Edge Computing Infrastructure Boom",
                            probability: 0.89,
                            impact: "+35-50%",
                            description: "Massive edge computing infrastructure deployment for real-time AI applications",
                            timeline: "July-September 2027"
                        },
                        {
                            event: "UK AI Sovereignty Initiative",
                            probability: 0.74,
                            impact: "+18-30%",
                            description: "UK government AI sovereignty initiative favoring domestic AI infrastructure investments",
                            timeline: "August 2027"
                        }
                    ]
                },
                sipp: {
                    amount: 15100,
                    change: "+£5,800",
                    catalysts: [
                        {
                            event: "Deep Sea Mining Approval Wave",
                            probability: 0.71,
                            impact: "+60-100%",
                            description: "International approval of deep sea mining for critical minerals revolutionizing supply",
                            timeline: "August 2027"
                        },
                        {
                            event: "Nuclear Fusion Infrastructure Investment",
                            probability: 0.66,
                            impact: "+45-80%",
                            description: "Major infrastructure investment in nuclear fusion supporting materials and technology",
                            timeline: "September 2027"
                        }
                    ]
                },
                gia: {
                    amount: 16800,
                    change: "+£7,100",
                    catalysts: [
                        {
                            event: "Autonomous Economy Launch",
                            probability: 0.81,
                            impact: "+45-70%",
                            description: "First fully autonomous economic zones launching with AI-driven growth companies",
                            timeline: "July 2027"
                        },
                        {
                            event: "Digital Currency Integration",
                            probability: 0.73,
                            impact: "+28-45%",
                            description: "Full digital currency integration enabling new growth business models",
                            timeline: "August-September 2027"
                        }
                    ]
                },
                crypto: {
                    amount: 4800,
                    change: "+£2,700",
                    catalysts: [
                        {
                            event: "Web3 Infrastructure Maturity",
                            probability: 0.88,
                            impact: "+110-190%",
                            description: "Web3 infrastructure reaching enterprise-grade maturity enabling mass adoption",
                            timeline: "July 2027"
                        },
                        {
                            event: "Quantum-Resistant Crypto Upgrade",
                            probability: 0.79,
                            impact: "+80-140%",
                            description: "Major cryptocurrencies successfully upgrading to quantum-resistant cryptography",
                            timeline: "September 2027"
                        }
                    ]
                },
                energy: {
                    amount: 1000,
                    change: "+£200",
                    catalysts: [
                        {
                            event: "Energy Storage Breakthrough",
                            probability: 0.77,
                            impact: "+25-40%",
                            description: "Major breakthrough in energy storage technology affecting traditional energy markets",
                            timeline: "August 2027"
                        },
                        {
                            event: "Geopolitical Energy Realignment",
                            probability: 0.62,
                            impact: "+30-55%",
                            description: "Major geopolitical realignment creating new energy supply chain opportunities",
                            timeline: "July-September 2027"
                        }
                    ]
                },
                speculative: {
                    amount: 800,
                    change: "+£400",
                    catalysts: [
                        {
                            event: "Consciousness Transfer Technology Demo",
                            probability: 0.19,
                            impact: "+2000-10000%",
                            description: "Breakthrough demonstration of consciousness transfer technology",
                            timeline: "September 2027"
                        },
                        {
                            event: "Molecular Assembly Manufacturing",
                            probability: 0.37,
                            impact: "+600-2000%",
                            description: "Molecular assembly manufacturing achieving commercial viability",
                            timeline: "August 2027"
                        }
                    ]
                }
            }
        },
        Q4: {
            totalDeployment: 49200,
            activeCatalysts: 30,
            expectedReturn: 47.1,
            riskLevel: "Very High",
            deployments: {
                isa: {
                    amount: 9100,
                    change: "+£4,800",
                    catalysts: [
                        {
                            event: "AI Infrastructure Consolidation",
                            probability: 0.91,
                            impact: "+40-60%",
                            description: "Major consolidation in AI infrastructure creating dominant platform players",
                            timeline: "October-December 2027"
                        },
                        {
                            event: "Quantum-AI Hybrid Systems",
                            probability: 0.68,
                            impact: "+32-55%",
                            description: "First commercial quantum-AI hybrid systems demonstrating exponential capabilities",
                            timeline: "November 2027"
                        }
                    ]
                },
                sipp: {
                    amount: 16800,
                    change: "+£6,400",
                    catalysts: [
                        {
                            event: "Asteroid Mining Commercial Launch",
                            probability: 0.58,
                            impact: "+80-150%",
                            description: "First commercial asteroid mining operation beginning rare earth extraction",
                            timeline: "November 2027"
                        },
                        {
                            event: "Climate Adaptation Infrastructure",
                            probability: 0.85,
                            impact: "+50-85%",
                            description: "Massive climate adaptation infrastructure requiring advanced materials and technology",
                            timeline: "December 2027"
                        }
                    ]
                },
                gia: {
                    amount: 18400,
                    change: "+£7,800",
                    catalysts: [
                        {
                            event: "Artificial General Intelligence Announcement",
                            probability: 0.43,
                            impact: "+100-200%",
                            description: "First credible artificial general intelligence system announcement revolutionizing growth stocks",
                            timeline: "December 2027"
                        },
                        {
                            event: "Global Economic AI Integration",
                            probability: 0.87,
                            impact: "+35-60%",
                            description: "Widespread AI integration into global economic systems boosting technology sectors",
                            timeline: "October-November 2027"
                        }
                    ]
                },
                crypto: {
                    amount: 4200,
                    change: "+£2,400",
                    catalysts: [
                        {
                            event: "Global Digital Asset Integration",
                            probability: 0.84,
                            impact: "+120-200%",
                            description: "Major economies fully integrating digital assets into financial systems",
                            timeline: "October 2027"
                        },
                        {
                            event: "Interplanetary Commerce Protocol",
                            probability: 0.31,
                            impact: "+500-2000%",
                            description: "First interplanetary commerce protocol using blockchain infrastructure",
                            timeline: "December 2027"
                        }
                    ]
                },
                energy: {
                    amount: 800,
                    change: "+£100",
                    catalysts: [
                        {
                            event: "Fusion Energy Commercial Deployment",
                            probability: 0.42,
                            impact: "+50-100%",
                            description: "First commercial fusion energy deployment creating energy market disruption",
                            timeline: "November 2027"
                        },
                        {
                            event: "Energy Independence Achievement",
                            probability: 0.76,
                            impact: "+20-40%",
                            description: "Major nations achieving energy independence through renewable and fusion technology",
                            timeline: "December 2027"
                        }
                    ]
                },
                speculative: {
                    amount: 900,
                    change: "+£500",
                    catalysts: [
                        {
                            event: "Time Dilation Technology Breakthrough",
                            probability: 0.08,
                            impact: "+10000-50000%",
                            description: "Theoretical breakthrough in time dilation technology with potential applications",
                            timeline: "December 2027"
                        },
                        {
                            event: "Biological Immortality Trial Results",
                            probability: 0.24,
                            impact: "+3000-15000%",
                            description: "Promising results from biological immortality clinical trials",
                            timeline: "November 2027"
                        }
                    ]
                }
            }
        }
    },
    2028: {
        Q1: {
            totalDeployment: 52700,
            activeCatalysts: 28,
            expectedReturn: 43.8,
            riskLevel: "Very High",
            deployments: {
                isa: {
                    amount: 10200,
                    change: "+£5,100",
                    catalysts: [
                        {
                            event: "Post-AGI Infrastructure Boom",
                            probability: 0.78,
                            impact: "+50-80%",
                            description: "Infrastructure boom following AGI deployment requiring massive compute resources",
                            timeline: "January-March 2028"
                        },
                        {
                            event: "Neural Interface Computing Integration",
                            probability: 0.64,
                            impact: "+38-65%",
                            description: "Brain-computer interfaces integrating with AI infrastructure creating new markets",
                            timeline: "February 2028"
                        }
                    ]
                },
                sipp: {
                    amount: 18100,
                    change: "+£6,800",
                    catalysts: [
                        {
                            event: "Extraterrestrial Mining Operations",
                            probability: 0.67,
                            impact: "+100-200%",
                            description: "Full-scale extraterrestrial mining operations revolutionizing material abundance",
                            timeline: "February 2028"
                        },
                        {
                            event: "Terraforming Technology Development",
                            probability: 0.45,
                            impact: "+80-150%",
                            description: "Advanced terraforming technology development requiring massive material investment",
                            timeline: "March 2028"
                        }
                    ]
                },
                gia: {
                    amount: 19800,
                    change: "+£8,200",
                    catalysts: [
                        {
                            event: "AGI Economic Integration",
                            probability: 0.82,
                            impact: "+60-100%",
                            description: "Full AGI integration into economic systems creating unprecedented growth opportunities",
                            timeline: "January 2028"
                        },
                        {
                            event: "Post-Scarcity Economic Transition",
                            probability: 0.56,
                            impact: "+80-150%",
                            description: "Early signs of post-scarcity economics revolutionizing growth investment paradigms",
                            timeline: "March 2028"
                        }
                    ]
                },
                crypto: {
                    amount: 3800,
                    change: "+£2,100",
                    catalysts: [
                        {
                            event: "Universal Basic Assets Protocol",
                            probability: 0.71,
                            impact: "+200-400%",
                            description: "Universal basic assets protocol using blockchain for resource distribution",
                            timeline: "January 2028"
                        },
                        {
                            event: "Galactic Commerce Network",
                            probability: 0.38,
                            impact: "+1000-5000%",
                            description: "First galactic commerce network using advanced blockchain infrastructure",
                            timeline: "February-March 2028"
                        }
                    ]
                },
                energy: {
                    amount: 600,
                    change: "+£50",
                    catalysts: [
                        {
                            event: "Fusion Energy Ubiquity",
                            probability: 0.73,
                            impact: "+30-60%",
                            description: "Fusion energy becoming ubiquitous, disrupting traditional energy investment thesis",
                            timeline: "January-March 2028"
                        },
                        {
                            event: "Antimatter Energy Research",
                            probability: 0.21,
                            impact: "+200-500%",
                            description: "Breakthrough antimatter energy research creating new energy paradigms",
                            timeline: "March 2028"
                        }
                    ]
                },
                speculative: {
                    amount: 1200,
                    change: "+£700",
                    catalysts: [
                        {
                            event: "Consciousness Uploading Success",
                            probability: 0.15,
                            impact: "+50000-200000%",
                            description: "Successful human consciousness uploading fundamentally changing humanity",
                            timeline: "March 2028"
                        },
                        {
                            event: "Reality Manipulation Technology",
                            probability: 0.05,
                            impact: "+100000-1000000%",
                            description: "Breakthrough in reality manipulation technology with infinite implications",
                            timeline: "January 2028"
                        }
                    ]
                }
            }
        }
    },
    2029: {
        Q1: {
            totalDeployment: 58900,
            activeCatalysts: 15,
            expectedReturn: 89.4,
            riskLevel: "Extreme",
            deployments: {
                isa: {
                    amount: 12000,
                    change: "+£8,200",
                    catalysts: [
                        {
                            event: "Post-Singularity Investment Paradigm",
                            probability: 0.91,
                            impact: "+200-500%",
                            description: "Investment paradigms adapting to post-technological singularity economic models",
                            timeline: "January-March 2029"
                        }
                    ]
                },
                sipp: {
                    amount: 25400,
                    change: "+£18,800",
                    catalysts: [
                        {
                            event: "Universal Material Abundance",
                            probability: 0.84,
                            impact: "+500-2000%",
                            description: "Universal material abundance through advanced manufacturing revolutionizing everything",
                            timeline: "February 2029"
                        }
                    ]
                },
                gia: {
                    amount: 18200,
                    change: "+£12,400",
                    catalysts: [
                        {
                            event: "Transhuman Economic Integration",
                            probability: 0.76,
                            impact: "+1000-5000%",
                            description: "Transhuman capabilities fully integrated into economic and investment systems",
                            timeline: "March 2029"
                        }
                    ]
                },
                crypto: {
                    amount: 2800,
                    change: "+£1,900",
                    catalysts: [
                        {
                            event: "Multiversal Currency Protocol",
                            probability: 0.43,
                            impact: "+10000-100000%",
                            description: "Currency protocol enabling trade across multiple reality dimensions",
                            timeline: "January-March 2029"
                        }
                    ]
                },
                energy: {
                    amount: 300,
                    change: "+£50",
                    catalysts: [
                        {
                            event: "Zero-Point Energy Mastery",
                            probability: 0.32,
                            impact: "+∞%",
                            description: "Mastery of zero-point energy making traditional energy investments obsolete",
                            timeline: "February 2029"
                        }
                    ]
                },
                speculative: {
                    amount: 200,
                    change: "+£100",
                    catalysts: [
                        {
                            event: "Omniscience Achievement",
                            probability: 0.08,
                            impact: "+∞%",
                            description: "Achievement of practical omniscience through advanced AI integration",
                            timeline: "March 2029"
                        }
                    ]
                }
            }
        }
    },
    2030: {
        Q1: {
            totalDeployment: 1000000,
            activeCatalysts: 1,
            expectedReturn: 999.9,
            riskLevel: "Transcendent",
            deployments: {
                isa: {
                    amount: 500000,
                    change: "+∞",
                    catalysts: [
                        {
                            event: "Economic Transcendence",
                            probability: 1.0,
                            impact: "+∞%",
                            description: "Complete transcendence of traditional economic models - post-scarcity civilization achieved",
                            timeline: "January-March 2030"
                        }
                    ]
                },
                sipp: {
                    amount: 500000,
                    change: "+∞",
                    catalysts: [
                        {
                            event: "Universal Prosperity Protocol",
                            probability: 1.0,
                            impact: "+∞%",
                            description: "Universal prosperity achieved through technological transcendence",
                            timeline: "January-March 2030"
                        }
                    ]
                },
                gia: {
                    amount: 0,
                    change: "Transcended",
                    catalysts: [
                        {
                            event: "Beyond Growth Paradigm",
                            probability: 1.0,
                            impact: "Transcendent",
                            description: "Growth investing becomes obsolete in post-scarcity transcendent economy",
                            timeline: "January 2030"
                        }
                    ]
                },
                crypto: {
                    amount: 0,
                    change: "Evolved",
                    catalysts: [
                        {
                            event: "Post-Currency Reality",
                            probability: 1.0,
                            impact: "Evolutionary",
                            description: "Currency and value exchange concepts evolve beyond current understanding",
                            timeline: "January 2030"
                        }
                    ]
                },
                energy: {
                    amount: 0,
                    change: "Infinite",
                    catalysts: [
                        {
                            event: "Infinite Energy Mastery",
                            probability: 1.0,
                            impact: "∞",
                            description: "Complete mastery of infinite energy sources making scarcity obsolete",
                            timeline: "January 2030"
                        }
                    ]
                },
                speculative: {
                    amount: 0,
                    change: "Realized",
                    catalysts: [
                        {
                            event: "Ultimate Reality Integration",
                            probability: 1.0,
                            impact: "∞",
                            description: "Integration with ultimate reality - all speculative investments become actualized",
                            timeline: "January 2030"
                        }
                    ]
                }
            }
        }
    }
};

// Global state management
let currentYear = 2026;
let currentQuarter = 'Q1';
let selectedPortfolio = 'all';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeTimeline();
    bindEventListeners();
    loadQuarterData(currentYear, currentQuarter);
});

function initializeTimeline() {
    // Set up initial UI state
    updateSummaryCards();

    // Initialize year and quarter tabs
    const yearTabs = document.querySelectorAll('.year-tab');
    const quarterTabs = document.querySelectorAll('.quarter-tab');

    yearTabs.forEach(tab => {
        if (tab.dataset.year === currentYear.toString()) {
            tab.classList.add('active');
        }
    });

    quarterTabs.forEach(tab => {
        if (tab.dataset.quarter === currentQuarter) {
            tab.classList.add('active');
        }
    });
}

function bindEventListeners() {
    // Year tab navigation
    document.querySelectorAll('.year-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            currentYear = parseInt(this.dataset.year);
            updateActiveTab('.year-tab', this);
            loadQuarterData(currentYear, currentQuarter);
        });
    });

    // Quarter tab navigation
    document.querySelectorAll('.quarter-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            currentQuarter = this.dataset.quarter;
            updateActiveTab('.quarter-tab', this);
            loadQuarterData(currentYear, currentQuarter);
        });
    });

    // Portfolio filter
    const portfolioFilter = document.getElementById('portfolioFilter');
    if (portfolioFilter) {
        portfolioFilter.addEventListener('change', function() {
            selectedPortfolio = this.value;
            loadQuarterData(currentYear, currentQuarter);
        });
    }

    // Export button
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportTimeline);
    }

    // Modal handling
    const modal = document.getElementById('catalystModal');
    const modalClose = document.getElementById('modalClose');

    if (modalClose) {
        modalClose.addEventListener('click', () => {
            modal.classList.remove('active');
        });
    }

    // Close modal on background click
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    }
}

function updateActiveTab(selector, activeTab) {
    document.querySelectorAll(selector).forEach(tab => tab.classList.remove('active'));
    activeTab.classList.add('active');
}

function loadQuarterData(year, quarter) {
    const timelineContent = document.getElementById('timelineContent');
    const quarterData = DEPLOYMENT_TIMELINE[year]?.[quarter];

    if (!quarterData) {
        timelineContent.innerHTML = `
            <div class="timeline-quarter">
                <div class="quarter-header">
                    <div class="quarter-title">${quarter} ${year}</div>
                    <div class="quarter-date-range">Coming Soon</div>
                </div>
                <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                    <h3>Timeline data for ${quarter} ${year} is being developed</h3>
                    <p>This quarter's deployment plan and catalyst analysis will be available soon.</p>
                </div>
            </div>
        `;
        return;
    }

    // Update summary cards
    updateSummaryCards(quarterData);

    // Generate quarter date range
    const dateRanges = {
        Q1: 'January - March',
        Q2: 'April - June',
        Q3: 'July - September',
        Q4: 'October - December'
    };

    let html = `
        <div class="timeline-quarter fade-in">
            <div class="quarter-header">
                <div class="quarter-title">${quarter} ${year}</div>
                <div class="quarter-date-range">${dateRanges[quarter]} ${year}</div>
                <div class="quarter-stats">
                    <div class="quarter-stat">
                        <div class="quarter-stat-value">£${quarterData.totalDeployment.toLocaleString()}</div>
                        <div>Total Deployment</div>
                    </div>
                    <div class="quarter-stat">
                        <div class="quarter-stat-value">${quarterData.activeCatalysts}</div>
                        <div>Active Catalysts</div>
                    </div>
                    <div class="quarter-stat">
                        <div class="quarter-stat-value">${quarterData.expectedReturn}%</div>
                        <div>Expected Return</div>
                    </div>
                    <div class="quarter-stat">
                        <div class="quarter-stat-value">${quarterData.riskLevel}</div>
                        <div>Risk Level</div>
                    </div>
                </div>
            </div>
            <div class="deployment-grid">
    `;

    // Filter and display portfolio deployments
    Object.entries(quarterData.deployments).forEach(([portfolioKey, deployment]) => {
        if (selectedPortfolio !== 'all' && selectedPortfolio !== portfolioKey) {
            return;
        }

        const portfolio = PORTFOLIO_DATA[portfolioKey];
        if (!portfolio) return;

        html += `
            <div class="portfolio-deployment">
                <div class="portfolio-header">
                    <div>
                        <div class="portfolio-title">${portfolio.name}</div>
                        <div class="portfolio-nickname">${portfolio.nickname}</div>
                    </div>
                    <div>
                        <div class="deployment-amount">£${deployment.amount.toLocaleString()}</div>
                        <div class="deployment-change">${deployment.change}</div>
                    </div>
                </div>
                <div class="catalyst-events">
        `;

        deployment.catalysts.forEach((catalyst, index) => {
            const probabilityClass = catalyst.probability >= 0.7 ? 'high' :
                                   catalyst.probability >= 0.5 ? 'medium' : 'low';

            html += `
                <div class="catalyst-event" onclick="showCatalystDetails('${portfolioKey}', ${index}, '${quarter}', ${year})">
                    <div class="catalyst-probability ${probabilityClass}">${Math.round(catalyst.probability * 100)}%</div>
                    <div class="catalyst-description">${catalyst.event}</div>
                    <div class="catalyst-impact">${catalyst.impact}</div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    });

    html += `
            </div>
        </div>
    `;

    timelineContent.innerHTML = html;
}

function updateSummaryCards(quarterData = null) {
    if (!quarterData) {
        // Use default values for initial load
        document.getElementById('totalCapital').textContent = '£76,872';
        document.getElementById('capitalChange').textContent = '+£24,247 this quarter';
        document.getElementById('activeCatalysts').textContent = '23';
        document.getElementById('catalystChange').textContent = '8 high-probability events';
        document.getElementById('expectedReturn').textContent = '+27.4%';
        document.getElementById('returnChange').textContent = 'Target range: 18-42%';
        return;
    }

    document.getElementById('totalCapital').textContent = `£${quarterData.totalDeployment.toLocaleString()}`;
    document.getElementById('capitalChange').textContent = `+£${(quarterData.totalDeployment * 0.45).toFixed(0)} this quarter`;
    document.getElementById('activeCatalysts').textContent = quarterData.activeCatalysts;

    const highProbCatalysts = Object.values(quarterData.deployments)
        .flatMap(d => d.catalysts)
        .filter(c => c.probability >= 0.7).length;
    document.getElementById('catalystChange').textContent = `${highProbCatalysts} high-probability events`;

    document.getElementById('expectedReturn').textContent = `+${quarterData.expectedReturn}%`;
    const minReturn = Math.max(0, quarterData.expectedReturn - 12);
    const maxReturn = quarterData.expectedReturn + 18;
    document.getElementById('returnChange').textContent = `Target range: ${minReturn}-${maxReturn}%`;
}

function showCatalystDetails(portfolioKey, catalystIndex, quarter, year) {
    const quarterData = DEPLOYMENT_TIMELINE[year]?.[quarter];
    if (!quarterData) return;

    const catalyst = quarterData.deployments[portfolioKey]?.catalysts[catalystIndex];
    const portfolio = PORTFOLIO_DATA[portfolioKey];

    if (!catalyst || !portfolio) return;

    const modal = document.getElementById('catalystModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalTitle.textContent = catalyst.event;

    const probabilityClass = catalyst.probability >= 0.7 ? 'high' :
                           catalyst.probability >= 0.5 ? 'medium' : 'low';
    const probabilityColor = catalyst.probability >= 0.7 ? 'var(--success)' :
                           catalyst.probability >= 0.5 ? 'var(--warning)' : 'var(--danger)';

    modalBody.innerHTML = `
        <div style="margin-bottom: 1.5rem;">
            <h4 style="color: var(--orange); margin-bottom: 0.5rem;">Portfolio</h4>
            <p>${portfolio.name} - ${portfolio.nickname}</p>
            <small style="color: var(--text-tertiary);">${portfolio.strategy}</small>
        </div>

        <div style="margin-bottom: 1.5rem;">
            <h4 style="color: var(--orange); margin-bottom: 0.5rem;">Event Details</h4>
            <p>${catalyst.description}</p>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
            <div>
                <h4 style="color: var(--orange); margin-bottom: 0.5rem;">Probability</h4>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="background: ${probabilityColor}; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-family: var(--font-mono); font-weight: 600;">
                        ${Math.round(catalyst.probability * 100)}%
                    </span>
                    <span style="color: var(--text-secondary); font-size: 0.875rem;">
                        ${catalyst.probability >= 0.7 ? 'High' : catalyst.probability >= 0.5 ? 'Medium' : 'Low'} Confidence
                    </span>
                </div>
            </div>
            <div>
                <h4 style="color: var(--orange); margin-bottom: 0.5rem;">Expected Impact</h4>
                <div style="color: var(--success); font-family: var(--font-mono); font-weight: 600; font-size: 1.1rem;">
                    ${catalyst.impact}
                </div>
            </div>
        </div>

        <div style="margin-bottom: 1.5rem;">
            <h4 style="color: var(--orange); margin-bottom: 0.5rem;">Timeline</h4>
            <p style="color: var(--text-secondary);">${catalyst.timeline}</p>
        </div>

        <div style="background: var(--surface-light); padding: 1rem; border-radius: var(--radius-sm); border-left: 3px solid var(--orange);">
            <h4 style="color: var(--orange); margin-bottom: 0.5rem;">Investment Thesis</h4>
            <p style="font-size: 0.875rem; color: var(--text-secondary);">
                This catalyst aligns with our ${portfolio.riskLevel.toLowerCase()} risk ${portfolio.timeHorizon} investment strategy.
                The ${Math.round(catalyst.probability * 100)}% probability assessment is based on current market conditions,
                regulatory environment, and historical precedent analysis.
            </p>
        </div>
    `;

    modal.classList.add('active');
}

function exportTimeline() {
    const exportData = {
        timestamp: new Date().toISOString(),
        currentView: {
            year: currentYear,
            quarter: currentQuarter,
            portfolio: selectedPortfolio
        },
        portfolioData: PORTFOLIO_DATA,
        deploymentData: DEPLOYMENT_TIMELINE[currentYear]?.[currentQuarter] || null
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

    const exportFileDefaultName = `nova-trader-timeline-${currentYear}-${currentQuarter}.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}