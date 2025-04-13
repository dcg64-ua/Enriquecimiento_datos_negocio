import argparse
from extractor import run_scraper
from kml_parser import parse_kml

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--kml', required=True)
    parser.add_argument('--query', required=True)
    parser.add_argument('--db', required=True)
    parser.add_argument('--deep', type=int, default=3)
    args = parser.parse_args()

    urls = parse_kml(args.kml)
    run_scraper(urls, args.query, args.db, args.deep)
